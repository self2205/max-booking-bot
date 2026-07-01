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


def change_status(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT status FROM bookings WHERE id=?",
        (booking_id,),
    )

    row = cursor.fetchone()

    if not row:
        conn.close()
        return

    status = row[0]

    if status == "🟢 Новая":
        new_status = "🟡 В работе"
    elif status == "🟡 В работе":
        new_status = "✅ Выполнена"
    else:
        new_status = "🟢 Новая"

    cursor.execute(
        "UPDATE bookings SET status=? WHERE id=?",
        (new_status, booking_id),
    )

    conn.commit()
    conn.close()


def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, product, name, phone, status, created_at
        FROM bookings
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows
