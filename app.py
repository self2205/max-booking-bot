from fastapi import FastAPI, Request
from pydantic import BaseModel
import sqlite3
from database import init_db, save_booking

app = FastAPI()

# Создаем базу при запуске
init_db()


class Booking(BaseModel):
    product: str
    name: str
    phone: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "MAX Booking Bot"
    }


@app.post("/booking")
async def booking(data: Booking):

    # Сохраняем в базу
    save_booking(
        data.product,
        data.name,
        data.phone
    )

    print("\n========== НОВАЯ ЗАЯВКА ==========")
    print(f"Товар: {data.product}")
    print(f"Имя: {data.name}")
    print(f"Телефон: {data.phone}")
    print("==================================\n")

    return {
        "success": True,
        "message": "Заявка сохранена"
    }


@app.get("/admin")
def admin():

    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, product, name, phone, created_at
        FROM bookings
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    html = """
    <html>
    <head>
        <title>Заявки</title>
        <style>
            body{
                font-family:Arial;
                padding:30px;
                background:#f5f5f5;
            }

            table{
                width:100%;
                border-collapse:collapse;
                background:white;
            }

            th,td{
                padding:12px;
                border:1px solid #ddd;
            }

            th{
                background:#222;
                color:white;
            }
        </style>
    </head>

    <body>

    <h2>Заявки магазина</h2>

    <table>

    <tr>
    <th>ID</th>
    <th>Товар</th>
    <th>Имя</th>
    <th>Телефон</th>
    <th>Дата</th>
    </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
        </tr>
        """

    html += """
    </table>

    </body>
    </html>
    """

    return html


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print(data)

    return {"ok": True}
