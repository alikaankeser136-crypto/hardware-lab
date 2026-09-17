import os
import secrets
from fastapi import FastAPI, HTTPException, Form, Depends, Request, status
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import get_db_connection, init_db

app = FastAPI(title="Hardware Lab")

# Session Middleware (Google OAuth ve Oturum için)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "hardware-lab-super-secret-key-12345"))

# Database ilklendirme
@app.on_event("startup")
def startup_event():
    init_db()

# Google OAuth Yapılandırması
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID", "dummy_id"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "dummy_secret"),
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
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = 'bakim_modu'").fetchone()
        conn.close()
        return row["deger"] == "1" if row else False
    except Exception:
        return False

# --- OAUTH ROTALARI ---

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
        return RedirectResponse(url="/", status_code=303)

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

# --- STATIK SAYFA ROTALARI ---

@app.get("/")
def home():
    if is_in_maintenance():
        return HTMLResponse(
            content="<h1>🛠️ Sitemiz Bakımdadır</h1><p>Kısa süre sonra tekrar ziyaret edin.</p>",
            headers=NO_CACHE_HEADERS
        )
    return FileResponse("index.html", headers=NO_CACHE_HEADERS)

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(username: str = Depends(check_admin)):
    return FileResponse("admin.html", headers=NO_CACHE_HEADERS)

# --- PUBLIC API ROTALARI ---

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

# İşlemci Karşılaştırma API
@app.get("/api/karsilastir/cpu")
def compare_cpus(cpu1: str, cpu2: str):
    conn = get_db_connection()
    c1 = conn.execute("SELECT * FROM cpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{cpu1.lower()}%",)).fetchone()
    c2 = conn.execute("SELECT * FROM cpus WHERE LOWER(isim) LIKE ? LIMIT 1", (f"%{cpu2.lower()}%",)).fetchone()
    conn.close()

    if not c1 or not c2:
        raise HTTPException(status_code=404, detail="İşlemcilerden biri bulunamadı.")

    fark = abs(c1["puan"] - c2["puan"])
    kazanan = c1["isim"] if c1["puan"] > c2["puan"] else c2["isim"]
    return {"cpu_1": dict(c1), "cpu_2": dict(c2), "kazanan": kazanan, "puan_farki": fark}

# Yorumları Getir
@app.get("/api/yorumlar/{parca_tipi}/{parca_id}")
def get_reviews(parca_tipi: str, parca_id: int):
    conn = get_db_connection()
    yorumlar = conn.execute(
        "SELECT * FROM yorumlar WHERE parca_tipi = ? AND parca_id = ? ORDER BY id DESC", 
        (parca_tipi.lower(), parca_id)
    ).fetchall()
    conn.close()
    return [dict(y) for y in yorumlar]

# Yorum & Yıldız Ekle
@app.post("/api/yorum-ekle")
def add_review(
    request: Request,
    parca_tipi: str = Form(...),
    parca_id: int = Form(...),
    yildiz: int = Form(...),
    yorum: str = Form(...)
):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Yorum yapmak için Google ile giriş yapmalısınız.")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO yorumlar (parca_tipi, parca_id, user_name, user_picture, yildiz, yorum) VALUES (?, ?, ?, ?, ?, ?)",
        (parca_tipi.lower(), parca_id, user.get('name', 'Kullanıcı'), user.get('picture', ''), yildiz, yorum)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Yorum kaydedildi."}
