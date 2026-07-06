import os
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


# ==========================
# INIT DATABASE
# ==========================
def init_db():

    conn = get_connection()
    cur = conn.cursor()


    # ======================
    # BOOKINGS
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (

            id SERIAL PRIMARY KEY,

            product TEXT NOT NULL,

            name TEXT NOT NULL,

            phone TEXT NOT NULL,

            image_url TEXT,

            status TEXT DEFAULT '🟢 Новая',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


    cur.execute("""
        ALTER TABLE bookings
        ADD COLUMN IF NOT EXISTS image_url TEXT;
    """)



    # ======================
    # PRODUCTS FOR MAX
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id TEXT PRIMARY KEY,

            product TEXT NOT NULL,

            image_url TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)



    conn.commit()

    cur.close()
    conn.close()



# ==========================
# SAVE BOOKING
# ==========================
def save_booking(
        product,
        name,
        phone,
        image_url=None
):

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        INSERT INTO bookings
        (
            product,
            name,
            phone,
            image_url
        )

        VALUES (%s, %s, %s, %s)

        RETURNING id

    """,
    (
        product,
        name,
        phone,
        image_url
    ))


    booking = cur.fetchone()


    conn.commit()

    cur.close()
    conn.close()


    print(
        f"✅ Заявка №{booking['id']} сохранена"
    )


    return booking["id"]



# ==========================
# GET BOOKINGS
# ==========================
def get_bookings():

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        SELECT
            id,
            product,
            name,
            phone,
            image_url,
            status,
            created_at

        FROM bookings

        ORDER BY id DESC

    """)


    rows = cur.fetchall()


    cur.close()
    conn.close()


    return rows



# ==========================
# CHANGE STATUS
# ==========================
def change_status(booking_id):

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        SELECT status
        FROM bookings
        WHERE id=%s

    """,
    (booking_id,))


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

    """,
    (
        new_status,
        booking_id
    ))


    conn.commit()

    cur.close()
    conn.close()



# =================================================
# PRODUCTS FOR MAX PAYLOAD
# =================================================


# ==========================
# SAVE PRODUCT
# ==========================
def save_product(
        product_id,
        product,
        image_url=None
):

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        INSERT INTO products
        (
            id,
            product,
            image_url
        )

        VALUES (%s, %s, %s)

        ON CONFLICT (id)

        DO UPDATE SET

            product = EXCLUDED.product,

            image_url = EXCLUDED.image_url

    """,
    (
        product_id,
        product,
        image_url
    ))


    conn.commit()

    cur.close()
    conn.close()



# ==========================
# GET PRODUCT
# ==========================
def get_product(product_id):

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        SELECT
            id,
            product,
            image_url

        FROM products

        WHERE id=%s

    """,
    (
        product_id,
    ))


    product = cur.fetchone()


    cur.close()
    conn.close()


    return product
