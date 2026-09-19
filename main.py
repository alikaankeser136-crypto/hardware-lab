import os
import secrets
import re
from fastapi import FastAPI, HTTPException, Form, Depends, Request, status
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import get_db_connection, init_db

app = FastAPI(title="Hardware Lab Benchmark API")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-key-hardware-lab"))

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

security = HTTPBasic()

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "1234")

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0"
}

def clean_query(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_correct = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass_correct = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_user_correct and is_pass_correct):
        raise HTTPException(status_code=401, detail="Yetkisiz", headers={"WWW-Authenticate": "Basic"})
    return credentials.username

def is_in_maintenance():
    conn = get_db_connection()
    row = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = 'bakim_modu'").fetchone()
    conn.close()
    return row["deger"] == "1" if row else False

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback", name="auth_google_callback")
async def auth_google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if user_info:
            request.session['user'] = dict(user_info)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Giriş hatası: {str(e)}")

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/me")
async def get_current_user(request: Request):
    user = request.session.get('user')
    if user:
        return {
            "authenticated": True, 
            "user": user,
            "name": user.get("name", user.get("given_name", "Kullanıcı")),
            "email": user.get("email")
        }
    return {"authenticated": False}

@app.get("/")
def home():
    if is_in_maintenance():
        return HTMLResponse("<h1>🛠️ Sitemiz Bakımdadır</h1>", headers=NO_CACHE_HEADERS)
    return FileResponse("index.html", headers=NO_CACHE_HEADERS)

# --- GOOGLE OYLAMA / PUAN VERME ---
@app.post("/api/rate")
async def rate_hardware(request: Request, donanim_tipi: str = Form(...), donanim_id: int = Form(...), puan: int = Form(...)):
    user = request.session.get('user')
    if not user or not user.get("email"):
        raise HTTPException(status_code=401, detail="Puan vermek için Google ile giriş yapmalısınız!")
    
    if puan < 1 or puan > 5:
        raise HTTPException(status_code=400, detail="Puan 1 ile 5 arasında olmalıdır.")

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO oy_sistemi (user_email, donanim_tipi, donanim_id, puan) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_email, donanim_tipi, donanim_id) 
            DO UPDATE SET puan = excluded.puan
        """, (user["email"], donanim_tipi, donanim_id, puan))
        conn.commit()
    finally:
        conn.close()
    
    return {"status": "success", "message": "Puanınız kaydedildi!"}

# --- PUBLIC APIS ---
@app.get("/api/gpus")
def get_all_gpus():
    conn = get_db_connection()
    gpus = conn.execute("SELECT * FROM gpus ORDER BY puan DESC").fetchall()
    conn.close()
    return [dict(g) for g in gpus]

@app.get("/api/cpus")
def get_all_cpus():
    conn = get_db_connection()
    cpus = conn.execute("SELECT * FROM cpus ORDER BY puan DESC").fetchall()
    conn.close()
    return [dict(c) for c in cpus]

# GPU KARŞILAŞTIRMA
@app.get("/api/karsilastir/gpu")
def compare_gpus(gpu1: str, gpu2: str):
    conn = get_db_connection()
    all_gpus = conn.execute("SELECT * FROM gpus").fetchall()
    conn.close()

    g1_q, g2_q = clean_query(gpu1), clean_query(gpu2)
    k1 = next((dict(g) for g in all_gpus if g1_q in clean_query(g["isim"])), None)
    k2 = next((dict(g) for g in all_gpus if g2_q in clean_query(g["isim"])), None)
    
    if not k1 or not k2:
        raise HTTPException(status_code=404, detail="Kartlardan biri bulunamadı")
        
    fark = abs(k1["puan"] - k2["puan"])
    yuzde = round((fark / min(k1["puan"], k2["puan"])) * 100, 1) if min(k1["puan"], k2["puan"]) > 0 else 0
    kazanan = k1["isim"] if k1["puan"] > k2["puan"] else k2["isim"]
    return {"item_1": k1, "item_2": k2, "kazanan": kazanan, "puan_farki": fark, "yuzde_fark": f"%{yuzde} daha hızlı"}

# CPU KARŞILAŞTIRMA
@app.get("/api/karsilastir/cpu")
def compare_cpus(cpu1: str, cpu2: str):
    conn = get_db_connection()
    all_cpus = conn.execute("SELECT * FROM cpus").fetchall()
    conn.close()

    c1_q, c2_q = clean_query(cpu1), clean_query(cpu2)
    k1 = next((dict(c) for c in all_cpus if c1_q in clean_query(c["isim"])), None)
    k2 = next((dict(c) for c in all_cpus if c2_q in clean_query(c["isim"])), None)
    
    if not k1 or not k2:
        raise HTTPException(status_code=404, detail="İşlemcilerden biri bulunamadı")
        
    fark = abs(k1["puan"] - k2["puan"])
    yuzde = round((fark / min(k1["puan"], k2["puan"])) * 100, 1) if min(k1["puan"], k2["puan"]) > 0 else 0
    kazanan = k1["isim"] if k1["puan"] > k2["puan"] else k2["isim"]
    return {"item_1": k1, "item_2": k2, "kazanan": kazanan, "puan_farki": fark, "yuzde_fark": f"%{yuzde} daha performanslı"}

# CPU + GPU İLE FPS HESAPLAYICI
@app.get("/api/fps")
def predict_fps(gpu: str, cpu: str = "", res: str = "1080p"):
    conn = get_db_connection()
    all_gpus = conn.execute("SELECT * FROM gpus").fetchall()
    all_cpus = conn.execute("SELECT * FROM cpus").fetchall()
    conn.close()

    g_obj = next((dict(g) for g in all_gpus if clean_query(gpu) in clean_query(g["isim"])), None)
    if not g_obj:
        raise HTTPException(status_code=404, detail="Ekran kartı bulunamadı")
        
    gpu_puan = g_obj["puan"]
    cpu_puan = gpu_puan # Varsayılan

    if cpu:
        c_obj = next((dict(c) for c in all_cpus if clean_query(cpu) in clean_query(c["isim"])), None)
        if c_obj:
            cpu_puan = c_obj["puan"]

    # Darboğaz hesabı faktörü
    faktör = min(1.0, cpu_puan / (gpu_puan * 0.9)) if gpu_puan > 0 else 1.0
    mult = 1.0 if res == "1080p" else (0.72 if res == "1440p" else 0.45)

    fps_verileri = {
        "Valorant (Low)": f"{max(30, int((gpu_puan * 0.038 + 180) * faktör * (1 if res=='1080p' else mult * 1.1)))} FPS",
        "CS2 (High)": f"{max(20, int((gpu_puan * 0.012 + 90) * faktör * mult))} FPS",
        "Cyberpunk 2077 (Ultra)": f"{max(10, int((gpu_puan * 0.0032 + 25) * mult))} FPS",
        "GTA V (Ultra)": f"{max(25, int((gpu_puan * 0.0045 + 60) * faktör * mult))} FPS"
    }
    return {"kart": g_obj["isim"], "cozunurluk": res.upper(), "oyunlar": fps_verileri}

# SİSTEM TOPLAMA VE UYUMLULUK ANALİZİ (CPU, GPU, RAM, SSD)
@app.post("/api/build-pc")
def build_pc(cpu_id: int = Form(...), gpu_id: int = Form(...), ram_gb: int = Form(...), ssd_gb: int = Form(...)):
    conn = get_db_connection()
    cpu = conn.execute("SELECT * FROM cpus WHERE id = ?", (cpu_id,)).fetchone()
    gpu = conn.execute("SELECT * FROM gpus WHERE id = ?", (gpu_id,)).fetchone()
    conn.close()

    if not cpu or not gpu:
        raise HTTPException(status_code=400, detail="Bileşen bulunamadı")

    toplam_puan = cpu["puan"] + gpu["puan"] + (ram_gb * 100)
    
    # Darboğaz Oranı
    oratio = cpu["puan"] / gpu["puan"]
    if oratio < 0.7:
        darbogaz_notu = "⚠️ İşlemciniz bu ekran kartının yanında biraz zayıf kalabilir (Darboğaz riski)."
    elif oratio > 1.4:
        darbogaz_notu = "ℹ️ Ekran kartınız işlemcinize göre zayıf kalıyor."
    else:
        darbogaz_notu = "🔥 Mükemmel Denge! CPU ve GPU tam uyumlu çalışır."

    return {
        "sistem_puani": toplam_puan,
        "cpu": cpu["isim"],
        "gpu": gpu["isim"],
        "ram": f"{ram_gb} GB RAM",
        "ssd": f"{ssd_gb} GB NVMe SSD",
        "degerlendirme": darbogaz_notu
    }
