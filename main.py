import os
import json
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel

from database import SessionLocal, init_db, HardwareItem, Review, User

app = FastAPI(title="Hardware Lab")

# Oturum yönetimi
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "hardware-lab-secret-key-12345"))

# Veritabanı tablolarını oluştur
init_db()

# Google OAuth Yapılandırması
oauth = OAuth()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "dummy_id")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "dummy_secret")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Template Dizini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=BASE_DIR)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Modelleri
class HardwareCreate(BaseModel):
    name: str
    category: str
    brand: str
    score: float
    specs: str

# Auth Rotaları
@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if user_info:
            user = db.query(User).filter(User.google_id == user_info['sub']).first()
            if not user:
                user = User(
                    google_id=user_info['sub'],
                    email=user_info['email'],
                    name=user_info['name'],
                    picture=user_info['picture']
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            request.session['user'] = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture
            }
    except Exception as e:
        print(f"Auth Error: {e}")
    return RedirectResponse(url='/')

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/')

# Ana Sayfa
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = request.session.get('user')
    hardware_list = db.query(HardwareItem).all()
    
    cpus = [item for item in hardware_list if item.category == 'CPU']
    gpus = [item for item in hardware_list if item.category == 'GPU']
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "cpus": cpus,
        "gpus": gpus,
        "hardware_list": hardware_list
    })

# API Endpoints
@app.post("/api/hardware")
async def create_hardware(item: HardwareCreate, db: Session = Depends(get_db)):
    new_item = HardwareItem(
        name=item.name,
        category=item.category,
        brand=item.brand,
        score=item.score,
        specs=item.specs
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"status": "success", "item": new_item.id}

@app.get("/api/compare")
async def compare_items(id1: int, id2: int, db: Session = Depends(get_db)):
    item1 = db.query(HardwareItem).filter(HardwareItem.id == id1).first()
    item2 = db.query(HardwareItem).filter(HardwareItem.id == id2).first()
    if not item1 or not item2:
        raise HTTPException(status_code=404, detail="Bileşen bulunamadı")
    
    def get_avg_rating(item):
        reviews = db.query(Review).filter(Review.hardware_id == item.id).all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

    return {
        "item1": {
            "id": item1.id,
            "name": item1.name,
            "category": item1.category,
            "brand": item1.brand,
            "specs": item1.specs,
            "score": item1.score,
            "rating": get_avg_rating(item1)
        },
        "item2": {
            "id": item2.id,
            "name": item2.name,
            "category": item2.category,
            "brand": item2.brand,
            "specs": item2.specs,
            "score": item2.score,
            "rating": get_avg_rating(item2)
        }
    }

@app.get("/api/hardware/{item_id}")
async def get_hardware_detail(item_id: int, db: Session = Depends(get_db)):
    item = db.query(HardwareItem).filter(HardwareItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bileşen bulunamadı")
    
    reviews = db.query(Review).filter(Review.hardware_id == item_id).all()
    review_list = []
    for r in reviews:
        u = db.query(User).filter(User.id == r.user_id).first()
        review_list.append({
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "user_name": u.name if u else "Anonim",
            "user_picture": u.picture if u else ""
        })
        
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "brand": item.brand,
        "specs": item.specs,
        "score": item.score,
        "reviews": review_list
    }

@app.post("/api/hardware/{item_id}/review")
async def add_review(
    item_id: int, 
    request: Request, 
    rating: int = Form(...), 
    comment: str = Form(...), 
    db: Session = Depends(get_db)
):
    user_data = request.session.get('user')
    if not user_data:
        raise HTTPException(status_code=401, detail="Lütfen önce giriş yapın.")
    
    new_review = Review(
        hardware_id=item_id,
        user_id=user_data['id'],
        rating=rating,
        comment=comment
    )
    db.add(new_review)
    db.commit()
    return {"status": "success", "message": "Yorum eklendi."}
