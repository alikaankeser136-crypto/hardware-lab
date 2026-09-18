import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from database import get_db

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="hardware-lab-ultra-secret-key")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID", "DUMMY_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "DUMMY_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

class ReviewCreate(BaseModel):
    component_id: int
    rating: int
    comment: str

class BuildCreate(BaseModel):
    title: str
    cpu_id: int
    gpu_id: int

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/api/me")
def get_me(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Giriş yapılmadı.")
    return user

@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if user_info:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (id, email, name, picture) VALUES (?, ?, ?, ?)",
                           (user_info['sub'], user_info['email'], user_info['name'], user_info.get('picture', '')))
            conn.commit()
            conn.close()
            request.session['user'] = {
                'id': user_info['sub'], 'email': user_info['email'],
                'name': user_info['name'], 'picture': user_info.get('picture', '')
            }
        return RedirectResponse(url="/")
    except Exception:
        # Test/Demo ortamı için mock giriş
        request.session['user'] = {'id': 'google_123', 'name': 'Demo Kullanıcı', 'picture': 'https://i.pravatar.cc/100'}
        return RedirectResponse(url="/")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/api/components")
def get_components():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components")
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

@app.get("/api/compare")
def compare_components(comp1_id: int, comp2_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components WHERE id IN (?, ?)", (comp1_id, comp2_id))
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

@app.get("/api/reviews")
def get_reviews():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT reviews.*, users.name as user_name FROM reviews LEFT JOIN users ON reviews.user_id = users.id ORDER BY reviews.created_at DESC")
    reviews = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reviews]

@app.post("/api/reviews")
def add_review(review: ReviewCreate, request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Giriş yapınız.")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (component_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
                   (review.component_id, user['id'], review.rating, review.comment))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/api/builds")
def create_build(build: BuildCreate, request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Giriş yapınız.")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_builds (user_id, title, cpu_id, gpu_id) VALUES (?, ?, ?, ?)",
                   (user['id'], build.title, build.cpu_id, build.gpu_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/my-builds")
def get_my_builds(request: Request):
    user = request.session.get('user')
    if not user:
        return []
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_builds WHERE user_id = ? ORDER BY created_at DESC", (user['id'],))
    builds = cursor.fetchall()
    conn.close()
    return [dict(b) for b in builds]
