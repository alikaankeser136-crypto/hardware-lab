import sqlite3

DB_NAME = "hardware.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ayarlar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO ayarlar (anahtar, deger) VALUES ('bakim_modu', '0')")

    # Ekran Kartları (GPUs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT UNIQUE,
            puan INTEGER,
            marka TEXT,
            vram TEXT,
            fiyat_performans TEXT
        )
    """)

    # İşlemciler (CPUs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT UNIQUE,
            puan INTEGER,
            marka TEXT,
            cekirdek TEXT,
            fiyat_performans TEXT
        )
    """)

    # Yorumlar ve Yıldız Puanları
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yorumlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parca_tipi TEXT,
            parca_id INTEGER,
            user_name TEXT,
            user_picture TEXT,
            yildiz INTEGER,
            yorum TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
