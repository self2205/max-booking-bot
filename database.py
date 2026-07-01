import sqlite3

DB_NAME = "bookings.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            name TEXT,
            phone TEXT,
            status TEXT DEFAULT '🟢 Новая',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Добавляем колонку status, если база уже существовала
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT '🟢 Новая'")
    except:
        pass

    conn.commit()
    conn.close()

def save_booking(product, name, phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO bookings(product, name, phone)
        VALUES (?, ?, ?)
        """,
        (product, name, phone),
    )

    conn.commit()
    conn.close()
