import sqlite3

def get_db():
    conn = sqlite3.connect("hardware.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Kullanıcılar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            picture TEXT
        )
    ''')
    
    # Donanımlar Tablosu
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

    # Yorumlar ve Puanlar Tablosu
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

    # Sistem Toplama Tablosu
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
    
    # Veritabanında donanım sayısı az ise geniş listeyi yükle
    cursor.execute("SELECT COUNT(*) FROM components")
    if cursor.fetchone()[0] < 100:
        # Önceki az veriyi temizle
        cursor.execute("DELETE FROM components")
        
        hardware_list = [
            # --- EKRAN KARTLARI (GPU) ---
            ('gpu', 'NVIDIA', 'GeForce RTX 4090', 100, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080 Super', 94, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080', 92, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti Super', 88, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti', 85, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Super', 82, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070', 78, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti 16GB', 72, '16 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti 8GB', 70, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060', 65, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3090 Ti', 86, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3090', 83, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 Ti', 81, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 12GB', 79, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 10GB', 77, '10 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3070 Ti', 71, '8 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3070', 68, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060 Ti', 63, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060 12GB', 55, '12 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3050 8GB', 42, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3050 6GB', 36, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080 Ti', 69, '11 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080 Super', 62, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080', 58, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2070 Super', 57, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2070', 52, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2060 Super', 50, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2060 6GB', 45, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660 Ti', 38, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660 Super', 37, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660', 33, '6 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1650 Super', 30, '4 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1650', 24, '4 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1080 Ti', 54, '11 GB GDDR5X'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1080', 44, '8 GB GDDR5X'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1070 Ti', 42, '8 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1070', 38, '8 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1060 6GB', 31, '6 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1060 3GB', 27, '3 GB GDDR5'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1050 Ti', 18, '4 GB GDDR5'),
            ('gpu', 'AMD', 'Radeon RX 7900 XTX', 93, '24 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7900 XT', 87, '20 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7900 GRE', 80, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7800 XT', 76, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7700 XT', 69, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7600 XT', 56, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7600', 52, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6950 XT', 82, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6900 XT', 79, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6800 XT', 74, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6800', 67, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6750 XT', 62, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6700 XT', 60, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6700 10GB', 55, '10 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6650 XT', 53, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6600 XT', 51, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6600', 46, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6500 XT', 26, '4 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A770 16GB', 54, '16 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A750', 49, '8 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A580', 44, '8 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A380', 21, '6 GB GDDR6'),

            # --- İŞLEMCİLER (CPU) ---
            ('cpu', 'AMD', 'Ryzen 9 7950X3D', 98, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7950X', 96, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900X3D', 93, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900X', 91, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900', 88, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7800X3D', 97, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7700X', 86, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7700', 84, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7600X', 80, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7600', 78, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7500F', 77, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 5800X3D', 85, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700X3D', 82, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 5950X', 89, '16C / 32T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 5900X', 84, '12C / 24T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5800X', 76, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700X', 74, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700G', 68, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600X', 70, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600', 68, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600G', 62, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5500', 60, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 4500', 52, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 3 4100', 42, '4C / 8T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 3900X', 73, '12C / 24T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 3700X', 63, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 3600', 55, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 2600', 42, '6C / 12T - AM4'),
            ('cpu', 'Intel', 'Core i9-14900KS', 100, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-14900K', 99, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-14900KF', 98, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-14700K', 94, '20C / 28T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-14700KF', 93, '20C / 28T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14600K', 87, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14600KF', 86, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14400F', 73, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-14100F', 58, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-13900KS', 97, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-13900K', 95, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-13700K', 90, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-13600K', 83, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-13400F', 71, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-13100F', 55, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-12900K', 88, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-12700K', 81, '12C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-12600K', 75, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-12400F', 66, '6C / 12T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-12100F', 52, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-11900K', 72, '8C / 16T - LGA1200'),
            ('cpu', 'Intel', 'Core i7-11700K', 67, '8C / 16T - LGA1200'),
            ('cpu', 'Intel', 'Core i5-11400F', 54, '6C / 12T - LGA1200'),
            ('cpu', 'Intel', 'Core i9-10900K', 70, '10C / 20T - LGA1200'),
            ('cpu', 'Intel', 'Core i7-10700K', 61, '8C / 16T - LGA1200'),
            ('cpu', 'Intel', 'Core i5-10400F', 48, '6C / 12T - LGA1200'),
            ('cpu', 'Intel', 'Core i7-3632QM', 18, '4C / 8T - Vaio Laptop')
        ]
        
        cursor.executemany("INSERT INTO components (type, brand, model, score, specs) VALUES (?, ?, ?, ?, ?)", hardware_list)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
