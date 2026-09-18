import sqlite3

def get_db():
    conn = sqlite3.connect("hardware.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Kullanıcılar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            picture TEXT
        )
    ''')
    
    # Donanımlar (CPU/GPU)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, -- 'cpu' veya 'gpu'
            brand TEXT,
            model TEXT,
            score INTEGER,
            specs TEXT
        )
    ''')

    # Yorumlar ve Puanlar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER,
            user_id TEXT,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(component_id) REFERENCES components(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Sistem Toplama (User Builds)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            cpu_id INTEGER,
            gpu_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Test için örnek donanım verisi yoksa ekle
    cursor.execute("SELECT COUNT(*) FROM components")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('cpu', 'AMD', 'Ryzen 5 5600', 85, '6 C / 12 T'),
            ('cpu', 'Intel', 'Core i5-12400F', 87, '6 C / 12 T'),
            ('gpu', 'NVIDIA', 'RTX 4060', 90, '8 GB VRAM'),
            ('gpu', 'AMD', 'RX 6700 XT', 88, '12 GB VRAM')
        ]
        cursor.executemany("INSERT INTO components (type, brand, model, score, specs) VALUES (?, ?, ?, ?, ?)", sample_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
