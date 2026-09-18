from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from database import get_db

app = FastAPI()

# --- Pydantic Modelleri ---
class ReviewCreate(BaseModel):
    component_id: int
    rating: int
    comment: str

class BuildCreate(BaseModel):
    title: str
    cpu_id: int
    gpu_id: int

# --- Oturum Kontrol Yardımcısı ---
def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Google ile giriş yapmalısınız.")
    return user

# --- Donanım Karşılaştırma API ---
@app.get("/api/compare")
def compare_components(comp1_id: int, comp2_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components WHERE id IN (?, ?)", (comp1_id, comp2_id))
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

# --- Yorum ve Puan Ekleme ---
@app.post("/api/reviews")
def add_review(review: ReviewCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reviews (component_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (review.component_id, user['sub'], review.rating, review.comment)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Yorum eklendi."}

# --- Sistem Toplama Özelliği ---
@app.post("/api/builds")
def create_build(build: BuildCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_builds (user_id, title, cpu_id, gpu_id) VALUES (?, ?, ?, ?)",
        (user['sub'], build.title, build.cpu_id, build.gpu_id)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Sistem kaydedildi."}

# --- Kullanıcının Kayıtlı Sistemleri ---
@app.get("/api/my-builds")
def get_my_builds(user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_builds WHERE user_id = ?", (user['sub'],))
    builds = cursor.fetchall()
    conn.close()
    return [dict(b) for b in builds]
