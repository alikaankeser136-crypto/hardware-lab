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
            specs TEXT -- JSON formatında ek teknik özellikler
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

    # Sistem Toplama (Custom Builds)
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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
