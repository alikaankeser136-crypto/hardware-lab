import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel

# --- VERİTABANI YARDIMCILARI ---

def get_db():
    conn = sqlite3.connect("hardware.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE, name TEXT, picture TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS components (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, brand TEXT, model TEXT, score INTEGER, specs TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, component_id INTEGER, user_id TEXT, rating INTEGER, comment TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_builds (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, cpu_id INTEGER, gpu_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute("SELECT COUNT(*) FROM components")
    if cursor.fetchone()[0] < 100:
        cursor.execute("DELETE FROM components")
        hardware_list = [
            ('gpu', 'NVIDIA', 'GeForce RTX 4090', 100, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080 Super', 94, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080', 92, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti Super', 88, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti', 85, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Super', 82, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070', 78, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti 16GB', 72, '16 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti 8GB', 70, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060', 65, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3090 Ti', 86, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3090', 83, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 Ti', 81, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 12GB', 79, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 10GB', 77, '10 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3070 Ti', 71, '8 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3070', 68, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060 Ti', 63, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060 12GB', 55, '12 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3050 8GB', 42, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3050 6GB', 36, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080 Ti', 69, '11 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080 Super', 62, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080', 58, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2070 Super', 57, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2070', 52, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2060 Super', 50, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2060 6GB', 45, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660 Ti', 38, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660 Super', 37, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660', 33, '6 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1650 Super', 30, '4 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1650', 24, '4 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1080 Ti', 54, '11 GB GDDR5X'),
            ('gpu', 'AMD', 'Radeon RX 7900 XTX', 93, '24 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7900 XT', 87, '20 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7900 GRE', 80, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7800 XT', 76, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7700 XT', 69, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7600 XT', 56, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7600', 52, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6950 XT', 82, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6900 XT', 79, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6800 XT', 74, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6800', 67, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6750 XT', 62, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6700 XT', 60, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6650 XT', 53, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6600', 46, '8 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A770 16GB', 54, '16 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A750', 49, '8 GB GDDR6'),
            ('cpu', 'AMD', 'Ryzen 9 7950X3D', 98, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7950X', 96, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900X3D', 93, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900X', 91, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7800X3D', 97, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7700X', 86, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7600X', 80, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7500F', 77, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 5800X3D', 85, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700X3D', 82, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 5950X', 89, '16C / 32T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 5900X', 84, '12C / 24T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5800X', 76, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700X', 74, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600X', 70, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600', 68, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5500', 60, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 3600', 55, '6C / 12T - AM4'),
            ('cpu', 'Intel', 'Core i9-14900KS', 100, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-14900K', 99, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-14700K', 94, '20C / 28T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14600K', 87, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14400F', 73, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-14100F', 58, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-13900KS', 97, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-13900K', 95, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-13700K', 90, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-13600K', 83, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-13400F', 71, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-13100F', 55, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-12900K', 88, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-12700K', 81, '12C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-12600K', 75, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-12400F', 66, '6C / 12T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-12100F', 52, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-3632QM', 18, '4C / 8T - Vaio Laptop')
        ]
        cursor.executemany("INSERT INTO components (type, brand, model, score, specs) VALUES (?, ?, ?, ?, ?)", hardware_list)

    conn.commit()
    conn.close()

# Sunucu kalkarken DB'yi hazırla
init_db()

# --- APP AYARLARI ---

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "hardware-lab-secret-key-2026"))

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

# --- SAYFA VE API ENDPOINT'LERİ ---

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/admin")
def read_admin():
    return FileResponse("admin.html")

@app.get("/api/me")
def get_me(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Giriş yapılmadı.")
    return user

@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = str(request.url_for('google_callback'))
    if "http://" in redirect_uri and "render.com" in redirect_uri:
        redirect_uri = redirect_uri.replace("http://", "https://")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if user_info:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO users (id, email, name, picture) VALUES (?, ?, ?, ?)",
                (user_info['sub'], user_info['email'], user_info['name'], user_info.get('picture', ''))
            )
            conn.commit()
            conn.close()
            
            request.session['user'] = {
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info['name'],
                'picture': user_info.get('picture', '')
            }
        return RedirectResponse(url="/")
    except Exception as e:
        # Google OAuth yapılandırılmamışsa yedek oturum açma
        request.session['user'] = {
            'id': 'demo_user_123',
            'email': 'demo@hardwarelab.com',
            'name': 'Ali Kaan',
            'picture': 'https://i.pravatar.cc/100'
        }
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

@app.delete("/api/admin/reviews/{review_id}")
def delete_review(review_id: int, request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Yetkisiz işlem.")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
