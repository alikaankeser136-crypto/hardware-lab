import sqlite3

DB_NAME = "donanim.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ekran Kartları Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            puan INTEGER NOT NULL,
            marka TEXT NOT NULL,
            vram TEXT NOT NULL,
            fiyat_performans TEXT NOT NULL
        )
    ''')

    # İşlemciler Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            puan INTEGER NOT NULL,
            marka TEXT NOT NULL,
            cekirdek TEXT NOT NULL,
            fiyat_performans TEXT NOT NULL
        )
    ''')

    # Oyun Gereksinimleri Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oyunlar (
            kod TEXT PRIMARY KEY,
            isim TEXT NOT NULL,
            gpu_min INTEGER NOT NULL,
            cpu_min INTEGER NOT NULL,
            ram_min INTEGER NOT NULL,
            gpu_rec INTEGER NOT NULL,
            cpu_rec INTEGER NOT NULL,
            ram_rec INTEGER NOT NULL
        )
    ''')

    # Ayarlar / Bakım Modu Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger TEXT NOT NULL
        )
    ''')

    # Varsayılan Bakım Modu Değeri ('0' = Yayında, '1' = Bakımda)
    cursor.execute("SELECT COUNT(*) FROM ayarlar WHERE anahtar = 'bakim_modu'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO ayarlar VALUES ('bakim_modu', '0')")

    # Tablo boşsa başlangıç verilerini doldur
    cursor.execute("SELECT COUNT(*) FROM gpus")
    if cursor.fetchone()[0] == 0:
        gpus_data = [
            ("Nvidia RTX 4090", 38800, "nvidia", "24 GB", "7/10"),
            ("AMD Radeon RX 7900 XTX", 31000, "amd", "24 GB", "8.5/10"),
            ("Nvidia RTX 4080 Super", 34500, "nvidia", "16 GB", "8/10"),
            ("AMD Radeon RX 7800 XT", 19500, "amd", "16 GB", "9.2/10"),
            ("Nvidia RTX 4070 Ti Super", 24200, "nvidia", "16 GB", "8.2/10"),
            ("Nvidia RTX 4060 Ti", 13800, "nvidia", "8 GB", "8/10"),
            ("AMD Radeon RX 6700 XT", 12800, "amd", "12 GB", "9.5/10"),
            ("Nvidia RTX 4060", 10500, "nvidia", "8 GB", "8.8/10"),
            ("AMD Radeon RX 7600", 10200, "amd", "8 GB", "8.7/10"),
            ("Nvidia RTX 3060", 8700, "nvidia", "12 GB", "9/10"),
            ("Nvidia RTX 2060", 7500, "nvidia", "6 GB", "8.5/10"),
            ("AMD Radeon RX 6600", 8100, "amd", "8 GB", "9.8/10"),
            ("Nvidia GTX 1650", 3500, "nvidia", "4 GB", "6/10")
        ]
        cursor.executemany("INSERT INTO gpus (isim, puan, marka, vram, fiyat_performans) VALUES (?, ?, ?, ?, ?)", gpus_data)

    cursor.execute("SELECT COUNT(*) FROM cpus")
    if cursor.fetchone()[0] == 0:
        cpus_data = [
            ("AMD Ryzen 7 7800X3D", 35500, "amd", "8 Çekirdek / 16 İzlek", "10/10"),
            ("Intel Core i9-14900K", 62400, "intel", "24 Çekirdek / 32 İzlek", "7.5/10"),
            ("Intel Core i7-13700K", 46500, "intel", "16 Çekirdek / 24 İzlek", "8.5/10"),
            ("Intel Core i5-13600K", 38200, "intel", "14 Çekirdek / 20 İzlek", "9.2/10"),
            ("AMD Ryzen 7 7700X", 36100, "amd", "8 Çekirdek / 16 İzlek", "8.8/10"),
            ("AMD Ryzen 5 7600X", 28500, "amd", "6 Çekirdek / 12 İzlek", "9.5/10"),
            ("AMD Ryzen 5 5600", 21800, "amd", "6 Çekirdek / 12 İzlek", "10/10"),
            ("Intel Core i5-12400F", 19800, "intel", "6 Çekirdek / 12 İzlek", "9.6/10"),
            ("Intel Core i3-12100F", 14200, "intel", "4 Çekirdek / 8 İzlek", "9/10")
        ]
        cursor.executemany("INSERT INTO cpus (isim, puan, marka, cekirdek, fiyat_performans) VALUES (?, ?, ?, ?, ?)", cpus_data)

    cursor.execute("SELECT COUNT(*) FROM oyunlar")
    if cursor.fetchone()[0] == 0:
        oyunlar_data = [
            ("valorant", "Valorant", 3000, 10000, 8, 7000, 18000, 16),
            ("cs2", "Counter-Strike 2", 4500, 12000, 8, 8500, 20000, 16),
            ("cyberpunk", "Cyberpunk 2077", 8000, 18000, 12, 19000, 30000, 16),
            ("gtav", "GTA V / Online", 3000, 8000, 8, 7000, 15000, 16),
            ("rdr2", "Red Dead Redemption 2", 7000, 15000, 12, 13000, 25000, 16)
        ]
        cursor.executemany("INSERT INTO oyunlar VALUES (?, ?, ?, ?, ?, ?, ?, ?)", oyunlar_data)

    conn.commit()
    conn.close()