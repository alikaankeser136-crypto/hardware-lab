import os
import secrets
from fastapi import FastAPI, HTTPException, Form, Depends, Request, status
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import get_db_connection, init_db

app = FastAPI()

# Session Middleware (OAuth state doğrulaması ve oturum tutmak için)
# Gerçek ortamda secret_key değerini gizli tutmalısın.
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-key-hardware-lab"))

# OAuth Yapılandırması
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

security = HTTPBasic()

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0"
}

def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_correct = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass_correct = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (is_user_correct and is_pass_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def is_in_maintenance():
    conn = get_db_connection()
    bakim = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = 'bakim_modu'").fetchone()["deger"]
    conn.close()
    return bakim == "1"

@app.on_event("startup")
def startup_event():
    init_db()

# --- GOOGLE AUTH ROTALARI ---

@app.get("/login/google")
async def login_via_google(request: Request):
    # Google Console'da belirttiğin callback adresiyle uyumlu şekilde yönlendirir
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
        return {"authenticated": True, "user": user}
    return {"authenticated": False}

# --- ANA SAYFA & DİĞER ROTALAR ---

@app.get("/")
def home():
    if is_in_maintenance():
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <title>Sitemiz Bakımdadır</title>
                <style>
                    body { background: #090d16; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
                    h1 { color: #f87171; font-size: 2.5rem; margin-bottom: 10px; }
                    p { color: #94a3b8; font-size: 1.1rem; }
                </style>
            </head>
            <body>
                <h1>🛠️ Sitemiz Geçici Olarak Bakımdadır</h1>
                <p>Donanım verilerimizi ve sistemimizi güncelliyoruz.<br>Lütfen kısa bir süre sonra tekrar ziyaret edin.</p>
            </body>
            </html>
            """,
            headers=NO_CACHE_HEADERS
        )
    return FileResponse("index.html", headers=NO_CACHE_HEADERS)

# --- ADMIN ROTALARI ---

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(username: str = Depends(check_admin)):
    return FileResponse("admin.html", headers=NO_CACHE_HEADERS)

@app.get("/api/admin/bakim-durumu")
def get_bakim_durumu(username: str = Depends(check_admin)):
    return {"bakim": "1" if is_in_maintenance() else "0"}

@app.post("/admin/toggle-maintenance")
def toggle_maintenance(username: str = Depends(check_admin)):
    conn = get_db_connection()
    mevcut = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = 'bakim_modu'").fetchone()["deger"]
    yeni_durum = "0" if mevcut == "1" else "1"
    conn.execute("UPDATE ayarlar SET deger = ? WHERE anahtar = 'bakim_modu'", (yeni_durum,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add-gpu")
def add_gpu(isim: str = Form(...), puan: int = Form(...), marka: str = Form(...), vram: str = Form(...), fiyat_performans: str = Form(...), username: str = Depends(check_admin)):
    conn = get_db_connection()
    conn.execute("INSERT INTO gpus (isim, puan, marka, vram, fiyat_performans) VALUES (?, ?, ?, ?, ?)",
                 (isim, puan, marka.lower(), vram, fiyat_performans))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add-cpu")
def add_cpu(isim: str = Form(...), puan: int = Form(...), marka: str = Form(...), cekirdek: str = Form(...), fiyat_performans: str = Form(...), username: str = Depends(check_admin)):
    conn = get_db_connection()
    conn.execute("INSERT INTO cpus (isim, puan, marka, cekirdek, fiyat_performans) VALUES (?, ?, ?, ?, ?)",
                 (isim, puan, marka.lower(), cekirdek, fiyat_performans))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/delete-gpu/{gpu_id}")
def delete_gpu(gpu_id: int, username: str = Depends(check_admin)):
    conn = get_db_connection()
    conn.execute("DELETE FROM gpus WHERE id = ?", (gpu_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/delete-cpu/{cpu_id}")
def delete_cpu(cpu_id: int, username: str = Depends(check_admin)):
    conn = get_db_connection()
    conn.execute("DELETE FROM cpus WHERE id = ?", (cpu_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)

# --- PUBLIC API ROTALARI ---

@app.get("/api/gpus")
def get_all_gpus():
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    gpus = conn.execute("SELECT * FROM gpus ORDER BY puan DESC").fetchall()
    conn.close()
    return [dict(g) for g in gpus]

@app.get("/api/gpu/{gpu_name}")
def search_gpu(gpu_name: str):
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    gpus = conn.execute("SELECT * FROM gpus WHERE LOWER(isim) LIKE ?", (f"%{gpu_name.lower()}%",)).fetchall()
    conn.close()
    return [dict(g) for g in gpus]

@app.get("/api/cpus")
def get_all_cpus():
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    cpus = conn.execute("SELECT * FROM cpus ORDER BY puan DESC").fetchall()
    conn.close()
    return [dict(c) for c in cpus]

@app.get("/api/cpu/{cpu_name}")
def search_cpu(cpu_name: str):
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    cpus = conn.execute("SELECT * FROM cpus WHERE LOWER(isim) LIKE ?", (f"%{cpu_name.lower()}%",)).fetchall()
    conn.close()
    return [dict(c) for c in cpus]

@app.get("/api/fps/{gpu_name}")
def predict_fps(gpu_name: str, res: str = "1080p"):
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    bulunan = conn.execute("SELECT * FROM gpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{gpu_name.lower()}%",)).fetchone()
    conn.close()

    if not bulunan:
        raise HTTPException(status_code=404, detail="Kart bulunamadı")
        
    puan = bulunan["puan"]
    mult = 1.0 if res == "1080p" else (0.72 if res == "1440p" else 0.45)

    fps_verileri = {
        "Valorant (Low/Comp)": f"{max(30, int((puan * 0.038 + 180) * (1 if res=='1080p' else mult * 1.1)))} FPS",
        "CS2 (Very High)": f"{max(20, int((puan * 0.012 + 90) * mult))} FPS",
        "Cyberpunk 2077 (Ultra)": f"{max(10, int((puan * 0.0032 + 25) * mult))} FPS",
        "GTA V (Very High)": f"{max(25, int((puan * 0.0045 + 60) * mult))} FPS",
        "RDR 2 (Ultra)": f"{max(15, int((puan * 0.0028 + 20) * mult))} FPS"
    }
    return {"kart": bulunan["isim"], "cozunurluk": res.upper(), "oyunlar": fps_verileri}

@app.get("/api/karsilastir")
def compare_gpus(gpu1: str, gpu2: str):
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    k1 = conn.execute("SELECT * FROM gpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{gpu1.lower()}%",)).fetchone()
    k2 = conn.execute("SELECT * FROM gpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{gpu2.lower()}%",)).fetchone()
    conn.close()
    
    if not k1 or not k2:
        raise HTTPException(status_code=404, detail="Kartlardan biri bulunamadı")
        
    fark = abs(k1["puan"] - k2["puan"])
    yuzde = round((fark / min(k1["puan"], k2["puan"])) * 100, 1)
    kazanan = k1["isim"] if k1["puan"] > k2["puan"] else k2["isim"]
    return {"kart_1": dict(k1), "kart_2": dict(k2), "kazanan": kazanan, "puan_farki": fark, "yuzde_fark": f"%{yuzde} daha hızlı"}

@app.get("/api/can-i-run")
def can_i_run(gpu: str, cpu: str, ram: int, game: str):
    if is_in_maintenance():
        raise HTTPException(status_code=503, detail="Sistem bakımdadır.")
    conn = get_db_connection()
    gpu_obj = conn.execute("SELECT * FROM gpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{gpu.lower()}%",)).fetchone()
    cpu_obj = conn.execute("SELECT * FROM cpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{cpu.lower()}%",)).fetchone()
    game_obj = conn.execute("SELECT * FROM oyunlar WHERE kod = ? LIMIT 1", (game.lower(),)).fetchone()
    conn.close()

    if not gpu_obj or not cpu_obj or not game_obj:
        raise HTTPException(status_code=404, detail="Bileşenler veya oyun bulunamadı")

    gpu_puan, cpu_puan = gpu_obj["puan"], cpu_obj["puan"]
    status, renk, detaylar = "ÖNERİLEN / ULTRA", "#34d399", []

    if gpu_puan < game_obj["gpu_min"]:
        status, renk = "KALDIRMAZ / ZORLANIR", "#f87171"
        detaylar.append(f"Ekran kartınız ({gpu_obj['isim']}) bu oyun için yetersiz kalabilir.")
    elif gpu_puan < game_obj["gpu_rec"]:
        status, renk = "MİNİMUM / DÜŞÜK AYARLAR", "#fbbf24"
        detaylar.append(f"Ekran kartınız minimum seviyede, düşük/orta ayarlarda oynayabilirsiniz.")

    if cpu_puan < game_obj["cpu_min"]:
        status, renk = "KALDIRMAZ / ZORLANIR", "#f87171"
        detaylar.append(f"İşlemciniz ({cpu_obj['isim']}) darboğaz yapabilir.")

    if ram < game_obj["ram_min"]:
        status, renk = "KALDIRMAZ / ZORLANIR", "#f87171"
        detaylar.append(f"RAM miktarınız ({ram} GB) minimum gereksinimden ({game_obj['ram_min']} GB) düşük.")

    if not detaylar:
        detaylar.append("Sisteminiz bu oyunu yüksek ayarlarda çalıştırmak için fazlasıyla yeterli! 🔥")

    return {"oyun": game_obj["isim"], "durum": status, "renk": renk, "detaylar": detaylar}
