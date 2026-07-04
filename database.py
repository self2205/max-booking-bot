import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            product TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT DEFAULT '🟢 Новая',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

    cur.close()
    conn.close()


def save_booking(product, name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bookings
        (product, name, phone)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        product,
        name,
        phone
    ))

    booking = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    print(f"✅ Заявка №{booking['id']} сохранена")

    return booking["id"]


def get_bookings():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            product,
            name,
            phone,
            status,
            created_at
        FROM bookings
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def change_status(booking_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT status
        FROM bookings
        WHERE id=%s
    """, (booking_id,))

    booking = cur.fetchone()

    if not booking:
        cur.close()
        conn.close()
        return

    status = booking["status"]

    if status == "🟢 Новая":
        new_status = "🟡 В работе"

    elif status == "🟡 В работе":
        new_status = "✅ Выполнена"

    else:
        new_status = "🟢 Новая"

    cur.execute("""
        UPDATE bookings
        SET status=%s
        WHERE id=%s
    """, (
        new_status,
        booking_id
    ))

    conn.commit()

    cur.close()
    conn.close()
