import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel

# --- VERİTABANI YAPILANDIRMASI ---

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_builds (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, cpu_id INTEGER, gpu_id INTEGER, mobo_id INTEGER, ram_id INTEGER, ssd_id INTEGER, psu_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute("SELECT COUNT(*) FROM components")
    if cursor.fetchone()[0] < 10:
        cursor.execute("DELETE FROM components")
        hardware_list = [
            # GPU
            ('gpu', 'NVIDIA', 'GeForce RTX 4090', 100, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080 Super', 94, '16 GB GDDR6X'),
            ('gpu', 'AMD', 'Radeon RX 7900 XTX', 93, '24 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti Super', 88, '16 GB GDDR6X'),
            ('gpu', 'AMD', 'Radeon RX 7800 XT', 76, '16 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti', 70, '8 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A770', 54, '16 GB GDDR6'),
            
            # CPU
            ('cpu', 'Intel', 'Core i9-14900KS', 100, '24C / 32T - LGA1700'),
            ('cpu', 'AMD', 'Ryzen 9 7950X3D', 98, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7800X3D', 97, '8C / 16T - AM5'),
            ('cpu', 'Intel', 'Core i7-14700K', 94, '20C / 28T - LGA1700'),
            ('cpu', 'AMD', 'Ryzen 5 7600X', 80, '6C / 12T - AM5'),
            ('cpu', 'Intel', 'Core i5-13400F', 71, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-3632QM', 18, '4C / 8T - Vaio Laptop'),

            # MOBO (Anakart)
            ('mobo', 'ASUS', 'ROG Maximus Z790 Hero', 98, 'LGA1700 DDR5 ATX'),
            ('mobo', 'MSI', 'MAG B650 Tomahawk WiFi', 88, 'AM5 DDR5 ATX'),
            ('mobo', 'Gigabyte', 'B760M AORUS ELITE', 78, 'LGA1700 DDR5 Micro-ATX'),

            # RAM
            ('ram', 'G.Skill', 'Trident Z5 RGB 32GB (2x16GB)', 95, 'DDR5 6000MHz CL30'),
            ('ram', 'Corsair', 'Vengeance LPX 16GB (2x8GB)', 75, 'DDR4 3200MHz CL16'),

            # SSD
            ('ssd', 'Samsung', '990 PRO 2TB', 99, 'PCIe 4.0 NVMe (7450 MB/s)'),
            ('ssd', 'Kingston', 'KC3000 1TB', 90, 'PCIe 4.0 NVMe (7000 MB/s)'),

            # PSU
            ('psu', 'Corsair', 'RM1000x 1000W', 96, '80+ Gold Tam Modüler'),
            ('psu', 'MSI', 'MAG A750GL 750W', 85, '80+ Gold PCIe 5.0')
        ]
        cursor.executemany("INSERT INTO components (type, brand, model, score, specs) VALUES (?, ?, ?, ?, ?)", hardware_list)

    conn.commit()
    conn.close()

init_db()

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
    mobo_id: int
    ram_id: int
    ssd_id: int
    psu_id: int

# --- API ENDPOINTS ---

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
            cursor.execute("INSERT OR REPLACE INTO users (id, email, name, picture) VALUES (?, ?, ?, ?)",
                           (user_info['sub'], user_info['email'], user_info['name'], user_info.get('picture', '')))
            conn.commit()
            conn.close()
            
            request.session['user'] = {
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info['name'],
                'picture': user_info.get('picture', '')
            }
        return RedirectResponse(url="/")
    except Exception:
        request.session['user'] = {'id': 'demo_user_123', 'email': 'demo@hardwarelab.com', 'name': 'Ali Kaan', 'picture': 'https://i.pravatar.cc/100'}
        return RedirectResponse(url="/")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/api/components")
def get_components():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components ORDER BY score DESC")
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
    cursor.execute("INSERT INTO user_builds (user_id, title, cpu_id, gpu_id, mobo_id, ram_id, ssd_id, psu_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (user['id'], build.title, build.cpu_id, build.gpu_id, build.mobo_id, build.ram_id, build.ssd_id, build.psu_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/all-builds")
def get_all_builds():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_builds.*, users.name as user_name FROM user_builds LEFT JOIN users ON user_builds.user_id = users.id ORDER BY created_at DESC")
    builds = cursor.fetchall()
    conn.close()
    return [dict(b) for b in builds]

# --- ADMİN SİLME ENDPOINT'LERİ ---

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

@app.delete("/api/admin/builds/{build_id}")
def delete_build(build_id: int, request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Yetkisiz işlem.")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_builds WHERE id = ?", (build_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
