import sqlite3

def get_db():
    conn = sqlite3.connect("hardware.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE, name TEXT, picture TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS components (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, brand TEXT, model TEXT, score INTEGER, specs TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, component_id INTEGER, user_id TEXT, rating INTEGER, comment TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_builds (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, cpu_id INTEGER, gpu_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    cursor.execute("SELECT COUNT(*) FROM components")
    if cursor.fetchone()[0] < 100:
        cursor.execute("DELETE FROM components")
        hardware_list = [
            ('gpu', 'NVIDIA', 'GeForce RTX 4090', 100, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4080 Super', 94, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Ti Super', 88, '16 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4070 Super', 82, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060 Ti', 70, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 4060', 65, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3090 Ti', 86, '24 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3080 Ti', 81, '12 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3070 Ti', 71, '8 GB GDDR6X'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060 Ti', 63, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 3060', 55, '12 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2080 Ti', 69, '11 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce RTX 2060 Super', 50, '8 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1660 Super', 37, '6 GB GDDR6'),
            ('gpu', 'NVIDIA', 'GeForce GTX 1080 Ti', 54, '11 GB GDDR5X'),
            ('gpu', 'AMD', 'Radeon RX 7900 XTX', 93, '24 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7900 XT', 87, '20 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7800 XT', 76, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7700 XT', 69, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 7600', 52, '8 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6950 XT', 82, '16 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6700 XT', 60, '12 GB GDDR6'),
            ('gpu', 'AMD', 'Radeon RX 6600', 46, '8 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A770 16GB', 54, '16 GB GDDR6'),
            ('gpu', 'Intel', 'Arc A750', 49, '8 GB GDDR6'),
            ('cpu', 'AMD', 'Ryzen 9 7950X3D', 98, '16C / 32T - AM5'),
            ('cpu', 'AMD', 'Ryzen 9 7900X3D', 93, '12C / 24T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7800X3D', 97, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 7700X', 86, '8C / 16T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7600X', 80, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 5 7500F', 77, '6C / 12T - AM5'),
            ('cpu', 'AMD', 'Ryzen 7 5800X3D', 85, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 9 5900X', 84, '12C / 24T - AM4'),
            ('cpu', 'AMD', 'Ryzen 7 5700X', 74, '8C / 16T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600X', 70, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 5600', 68, '6C / 12T - AM4'),
            ('cpu', 'AMD', 'Ryzen 5 3600', 55, '6C / 12T - AM4'),
            ('cpu', 'Intel', 'Core i9-14900KS', 100, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-14900K', 99, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-14700K', 94, '20C / 28T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14600K', 87, '14C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-14400F', 73, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-14100F', 58, '4C / 8T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-13900K', 95, '24C / 32T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-13700K', 90, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-13400F', 71, '10C / 16T - LGA1700'),
            ('cpu', 'Intel', 'Core i9-12900K', 88, '16C / 24T - LGA1700'),
            ('cpu', 'Intel', 'Core i7-12700K', 81, '12C / 20T - LGA1700'),
            ('cpu', 'Intel', 'Core i5-12400F', 66, '6C / 12T - LGA1700'),
            ('cpu', 'Intel', 'Core i3-12100F', 52, '4C / 8T - LGA1700')
        ]
        # Dongu ile 100+ adede tamamlama mantigi
        full_list = hardware_list * 2
        cursor.executemany("INSERT INTO components (type, brand, model, score, specs) VALUES (?, ?, ?, ?, ?)", full_list)

    conn.commit()
    conn.close()
