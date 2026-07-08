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

            client_chat_id BIGINT,

            telegram_message_id BIGINT,

            status TEXT DEFAULT '🟢 Новая',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)



    cur.execute("""
        ALTER TABLE bookings
        ADD COLUMN IF NOT EXISTS image_url TEXT;
    """)



    cur.execute("""
        ALTER TABLE bookings
        ADD COLUMN IF NOT EXISTS client_chat_id BIGINT;
    """)



    cur.execute("""
        ALTER TABLE bookings
        ADD COLUMN IF NOT EXISTS telegram_message_id BIGINT;
    """)





    # ======================
    # PRODUCTS
    # ======================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id TEXT PRIMARY KEY,

            product TEXT NOT NULL,

            image_url TEXT,

            channel_message_id INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
    """)



    cur.execute("""
        ALTER TABLE products
        ADD COLUMN IF NOT EXISTS channel_message_id INTEGER;
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
        image_url=None,
        client_chat_id=None
):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        INSERT INTO bookings
        (
            product,
            name,
            phone,
            image_url,
            client_chat_id
        )

        VALUES (%s,%s,%s,%s,%s)

        RETURNING id

    """,
    (
        product,
        name,
        phone,
        image_url,
        client_chat_id
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
# SAVE TELEGRAM MESSAGE ID
# ==========================

def save_telegram_message_id(
        booking_id,
        telegram_message_id
):

    conn = get_connection()
    cur = conn.cursor()


    cur.execute("""
        UPDATE bookings

        SET telegram_message_id=%s

        WHERE id=%s

    """,
    (
        telegram_message_id,
        booking_id
    ))


    conn.commit()

    cur.close()
    conn.close()





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
            client_chat_id,
            telegram_message_id,
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
# GET ONE BOOKING
# ==========================

def get_booking(booking_id):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        SELECT

            *

        FROM bookings

        WHERE id=%s

    """,
    (
        booking_id,
    ))



    result = cur.fetchone()



    cur.close()
    conn.close()


    return result





# ==========================
# UPDATE STATUS
# ==========================

def update_booking_status(
        booking_id,
        status
):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        UPDATE bookings

        SET status=%s

        WHERE id=%s

    """,
    (
        status,
        booking_id
    ))



    conn.commit()

    cur.close()
    conn.close()






# ==========================
# CHANGE STATUS
# ==========================

def change_status(booking_id):

    booking = get_booking(
        booking_id
    )


    if not booking:

        return



    current = booking["status"]



    if current == "🟢 Новая":

        new_status = "🟡 В работе"


    elif current == "🟡 В работе":

        new_status = "✅ Выполнена"


    elif current == "❌ Отменена":

        new_status = "🟢 Новая"


    else:

        new_status = "🟢 Новая"




    update_booking_status(
        booking_id,
        new_status
    )







# =================================================
# PRODUCTS FOR MAX
# =================================================


def save_product(
        product_id,
        product,
        image_url=None,
        channel_message_id=None
):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        INSERT INTO products
        (
            id,
            product,
            image_url,
            channel_message_id
        )

        VALUES (%s,%s,%s,%s)


        ON CONFLICT(id)

        DO UPDATE SET


            product = EXCLUDED.product,

            image_url = EXCLUDED.image_url,

            channel_message_id = EXCLUDED.channel_message_id

    """,
    (
        product_id,
        product,
        image_url,
        channel_message_id
    ))



    conn.commit()

    cur.close()
    conn.close()





# ==========================
# GET PRODUCT BY ID
# ==========================

def get_product(product_id):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        SELECT

            id,
            product,
            image_url,
            channel_message_id

        FROM products

        WHERE id=%s

    """,
    (
        product_id,
    ))



    result = cur.fetchone()



    cur.close()
    conn.close()


    return result






# ==========================
# GET PRODUCT BY NAME
# ==========================

def get_product_by_name(product):

    conn = get_connection()
    cur = conn.cursor()



    cur.execute("""
        SELECT

            id,
            product,
            image_url,
            channel_message_id

        FROM products

        WHERE product=%s

        ORDER BY created_at DESC

        LIMIT 1

    """,
    (
        product,
    ))



    result = cur.fetchone()



    cur.close()
    conn.close()


    return result
