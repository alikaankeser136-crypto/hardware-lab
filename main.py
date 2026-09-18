import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from database import get_db, init_db

app = FastAPI()

# Oturum yönetimi için gizli anahtar (Varsa var olan anahtarınızla değiştirin)
app.add_middleware(SessionMiddleware, secret_key="hardware-lab-secret-key")

# Veritabanını başlat
init_db()

# --- Pydantic Veri Modelleri ---
class ReviewCreate(BaseModel):
    component_id: int
    rating: int
    comment: str

class BuildCreate(BaseModel):
    title: str
    cpu_id: int
    gpu_id: int

# --- Oturum Kontrolü ---
def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Google ile giriş yapmalısınız.")
    return user

# --- Ana Sayfa Servisi ---
@app.get("/")
def read_root():
    return FileResponse("index.html")

# --- Kullanıcı Bilgisi ---
@app.get("/api/me")
def get_me(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Giriş yapılmadı.")
    return user

# --- Donanım Listesi ---
@app.get("/api/components")
def get_components():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components")
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

# --- Karşılaştırma API ---
@app.get("/api/compare")
def compare_components(comp1_id: int, comp2_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components WHERE id IN (?, ?)", (comp1_id, comp2_id))
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

# --- Yorumları Listeleme ---
@app.get("/api/reviews")
def get_reviews():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reviews.*, users.name as user_name 
        FROM reviews 
        LEFT JOIN users ON reviews.user_id = users.id 
        ORDER BY reviews.created_at DESC
    """)
    reviews = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reviews]

# --- Yorum & Puan Ekleme ---
@app.post("/api/reviews")
def add_review(review: ReviewCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reviews (component_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (review.component_id, user['id'], review.rating, review.comment)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Yorum eklendi."}

# --- Sistem Toplama Ekleme ---
@app.post("/api/builds")
def create_build(build: BuildCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_builds (user_id, title, cpu_id, gpu_id) VALUES (?, ?, ?, ?)",
        (user['id'], build.title, build.cpu_id, build.gpu_id)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Sistem kaydedildi."}

# --- Kullanıcının Kayıtlı Sistemlerini Listeleme ---
@app.get("/api/my-builds")
def get_my_builds(user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_builds WHERE user_id = ? ORDER BY created_at DESC", (user['id'],))
    builds = cursor.fetchall()
    conn.close()
    return [dict(b) for b in builds]
