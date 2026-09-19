import sqlite3

DB_NAME = "hardware.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # GPU Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gpus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT NOT NULL,
        puan INTEGER NOT NULL,
        marka TEXT NOT NULL,
        vram TEXT NOT NULL,
        fiyat_performans TEXT NOT NULL
    )
    """)

    # CPU Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cpus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT NOT NULL,
        puan INTEGER NOT NULL,
        marka TEXT NOT NULL,
        cekirdek TEXT NOT NULL,
        fiyat_performans TEXT NOT NULL
    )
    """)

    # Kullanıcı Değerlendirmeleri (Google Oylama) Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oy_sistemi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        donanim_tipi TEXT NOT NULL, -- 'gpu' veya 'cpu'
        donanim_id INTEGER NOT NULL,
        puan INTEGER NOT NULL,
        UNIQUE(user_email, donanim_tipi, donanim_id)
    )
    """)

    # Oyun Gereksinimleri
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oyunlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kod TEXT UNIQUE NOT NULL,
        isim TEXT NOT NULL,
        gpu_min INTEGER,
        gpu_rec INTEGER,
        cpu_min INTEGER,
        cpu_rec INTEGER,
        ram_min INTEGER
    )
    """)

    # Ayarlar Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ayarlar (
        anahtar TEXT PRIMARY KEY,
        deger TEXT
    )
    """)
    cursor.execute("INSERT OR IGNORE INTO ayarlar (anahtar, deger) VALUES ('bakim_modu', '0')")

    # Başlangıç Verilerini Ekle (Genişletilmiş Parça Listesi)
    gpu_count = cursor.execute("SELECT COUNT(*) FROM gpus").fetchone()[0]
    if gpu_count == 0:
        gpus = [
            ("NVIDIA RTX 4090", 38500, "nvidia", "24 GB", "8.2/10"),
            ("NVIDIA RTX 4080 Super", 31000, "nvidia", "16 GB", "8.8/10"),
            ("AMD Radeon RX 7900 XTX", 29500, "amd", "24 GB", "9.1/10"),
            ("NVIDIA RTX 4070 Ti Super", 25500, "nvidia", "16 GB", "9.0/10"),
            ("AMD Radeon RX 7900 XT", 24000, "amd", "20 GB", "9.2/10"),
            ("NVIDIA RTX 4070 Super", 21500, "nvidia", "12 GB", "9.5/10"),
            ("NVIDIA RTX 4070", 19000, "nvidia", "12 GB", "9.1/10"),
            ("AMD Radeon RX 7800 XT", 18500, "amd", "16 GB", "9.7/10"),
            ("NVIDIA RTX 3080 Ti", 17500, "nvidia", "12 GB", "8.5/10"),
            ("NVIDIA RTX 4060 Ti", 14000, "nvidia", "8 GB", "8.3/10"),
            ("AMD Radeon RX 6700 XT", 12500, "amd", "12 GB", "9.8/10"),
            ("NVIDIA RTX 4060", 12000, "nvidia", "8 GB", "8.9/10"),
            ("NVIDIA RTX 3060 Ti", 11500, "nvidia", "8 GB", "8.7/10"),
            ("NVIDIA RTX 3060", 9500, "nvidia", "12 GB", "9.0/10"),
            ("AMD Radeon RX 6600", 8200, "amd", "8 GB", "9.6/10"),
            ("NVIDIA GTX 1660 Super", 6000, "nvidia", "6 GB", "8.5/10"),
            ("NVIDIA GTX 1650", 3800, "nvidia", "4 GB", "7.5/10"),
        ]
        cursor.executemany("INSERT INTO gpus (isim, puan, marka, vram, fiyat_performans) VALUES (?, ?, ?, ?, ?)", gpus)

    cpu_count = cursor.execute("SELECT COUNT(*) FROM cpus").fetchone()[0]
    if cpu_count == 0:
        cpus = [
            ("AMD Ryzen 7 7800X3D", 35000, "amd", "8C / 16T", "9.9/10"),
            ("Intel Core i9-14900K", 34500, "intel", "24C / 32T", "8.4/10"),
            ("AMD Ryzen 9 7950X3D", 34000, "amd", "16C / 32T", "8.8/10"),
            ("Intel Core i7-14700K", 31000, "intel", "20C / 28T", "9.1/10"),
            ("AMD Ryzen 7 9700X", 29000, "amd", "8C / 16T", "9.0/10"),
            ("Intel Core i5-14600K", 26000, "intel", "14C / 20T", "9.3/10"),
            ("AMD Ryzen 5 7600X", 21000, "amd", "6C / 12T", "9.5/10"),
            ("Intel Core i5-13400F", 16000, "intel", "10C / 16T", "9.2/10"),
            ("AMD Ryzen 7 5800X3D", 22000, "amd", "8C / 16T", "9.6/10"),
            ("AMD Ryzen 5 5600X", 14500, "amd", "6C / 12T", "9.4/10"),
            ("AMD Ryzen 5 5600", 14000, "amd", "6C / 12T", "9.8/10"),
            ("Intel Core i5-12400F", 13800, "intel", "6C / 12T", "9.6/10"),
            ("AMD Ryzen 5 3600", 9500, "amd", "6C / 12T", "8.9/10"),
            ("Intel Core i3-12100F", 9000, "intel", "4C / 8T", "9.7/10"),
        ]
        cursor.executemany("INSERT INTO cpus (isim, puan, marka, cekirdek, fiyat_performans) VALUES (?, ?, ?, ?, ?)", cpus)

    game_count = cursor.execute("SELECT COUNT(*) FROM oyunlar").fetchone()[0]
    if game_count == 0:
        oyunlar = [
            ("valorant", "Valorant", 3000, 8000, 3000, 8000, 8),
            ("cs2", "Counter-Strike 2", 5000, 12000, 5000, 12000, 8),
            ("cyberpunk", "Cyberpunk 2077", 10000, 22000, 10000, 22000, 16),
            ("gtav", "GTA V", 4000, 9000, 4000, 9000, 8),
            ("rdr2", "Red Dead Redemption 2", 8000, 18000, 8000, 18000, 12)
        ]
        cursor.executemany("INSERT INTO oyunlar (kod, isim, gpu_min, gpu_rec, cpu_min, cpu_rec, ram_min) VALUES (?, ?, ?, ?, ?, ?, ?)", oyunlar)

    conn.commit()
    conn.close()
