from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import secrets
import requests
import urllib3

from database import init_db, save_booking
from booking_service import create_booking
from telegram_service import send_to_telegram
from max_service import send_message_max
from config import *

app = FastAPI()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================
# INIT DB
# ==========================
init_db()


# ==========================
# AUTH
# ==========================
security = HTTPBasic()

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    login_ok = secrets.compare_digest(credentials.username, ADMIN_LOGIN)
    password_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (login_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong login",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


# ==========================
# MODEL
# ==========================
class Booking(BaseModel):
    product: str
    name: str
    phone: str


# ==========================
# ROOT
# ==========================
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "MAX Booking Bot"
    }


# ==========================
# BOOKING
# ==========================
@app.post("/booking")
def booking(data: Booking):

    create_booking(
        data.product,
        data.name,
        data.phone
    )

    return {"success": True}

# ==========================
# WEBHOOK
# ==========================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("========== MAX EVENT ==========")
    print(data)
    print("================================")

    message = data.get("message", {})
    text = message.get("body", {}).get("text")

    print("DEBUG message:", text)

    if text == "/start":
        send_message_max(
            data,
            "Привет 👋\n\nЯ бот бронирования магазина."
        )

    elif text:
        send_message_max(
            data,
            f"Ты написал: {text}"
        )

    return {"ok": True}
    # ==========================
# ADMIN PANEL
# ==========================
@app.get("/admin", response_class=HTMLResponse)
def admin(auth: bool = Depends(check_auth)):

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
<!DOCTYPE html>
<html lang="ru">

<head>
<meta charset="UTF-8">
<title>Заявки магазина</title>

<style>

body{
    font-family:Arial,sans-serif;
    background:#f5f5f5;
    margin:40px;
}

h2{
    margin-bottom:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    background:white;
}

th{
    background:#222;
    color:white;
    padding:12px;
}

td{
    border:1px solid #ddd;
    padding:12px;
}

tr:nth-child(even){
    background:#f8f8f8;
}

</style>

</head>

<body>

<h2>📋 Заявки магазина</h2>

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

    return HTMLResponse(content=html)
