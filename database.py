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

    # Bakım modu varsayılanı
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
            parca_tipi TEXT, -- 'gpu' veya 'cpu'
            parca_id INTEGER,
            user_name TEXT,
            user_picture TEXT,
            yildiz INTEGER,
            yorum TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Örnek veriler ekle (Boşsa)
    cursor.execute("SELECT COUNT(*) FROM gpus")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO gpus (isim, puan, marka, vram, fiyat_performans) VALUES ('NVIDIA RTX 4090', 38000, 'nvidia', '24 GB', '7.5/10')")
        cursor.execute("INSERT INTO gpus (isim, puan, marka, vram, fiyat_performans) VALUES ('NVIDIA RTX 4070 Super', 21500, 'nvidia', '12 GB', '9.0/10')")

    cursor.execute("SELECT COUNT(*) FROM cpus")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO cpus (isim, puan, marka, cekirdek, fiyat_performans) VALUES ('AMD Ryzen 7 7800X3D', 34000, 'amd', '8 Çekirdek', '9.8/10')")
        cursor.execute("INSERT INTO cpus (isim, puan, marka, cekirdek, fiyat_performans) VALUES ('Intel Core i5-13600K', 28500, 'intel', '14 Çekirdek', '8.9/10')")

    conn.commit()
    conn.close()
