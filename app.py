from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

import secrets

from config import *
from database import init_db, get_bookings, change_status
from booking_service import create_booking
from max_service import send_message_max

app = FastAPI()

# ==========================
# INIT DATABASE
# ==========================
init_db()

# ==========================
# AUTH
# ==========================
security = HTTPBasic()


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    login_ok = secrets.compare_digest(
        credentials.username,
        ADMIN_LOGIN
    )

    password_ok = secrets.compare_digest(
        credentials.password,
        ADMIN_PASSWORD
    )

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
# BOOKING API
# ==========================
@app.post("/booking")
def booking(data: Booking):

    booking_id = create_booking(
        product=data.product,
        name=data.name,
        phone=data.phone
    )

    return {
        "success": True,
        "booking_id": booking_id
    }


# ==========================
# WEBHOOK MAX
# ==========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("\n========== MAX EVENT ==========")
    print(data)
    print("================================\n")

    message = data.get("message", {})
    text = message.get("body", {}).get("text", "").strip()

    print("DEBUG message:", text)

    if text == "/start":

        send_message_max(
            data,
            "👋 Добро пожаловать!\n\n"
            "Я помогу вам забронировать товар."
        )

    elif text:

        send_message_max(
            data,
            f"Вы написали:\n\n{text}"
        )

    return {
        "ok": True
    }
    
# ==========================
# ADMIN PANEL
# ==========================
@app.get("/admin", response_class=HTMLResponse)
def admin(auth: bool = Depends(check_auth)):

    rows = get_bookings()

    html = """
<!DOCTYPE html>
<html lang="ru">

<head>
<meta charset="UTF-8">
<title>Заявки</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    margin: 40px;
}

h2 {
    margin-bottom: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

th {
    background: #222;
    color: white;
    padding: 12px;
    text-align: left;
}

td {
    border: 1px solid #ddd;
    padding: 12px;
}

tr:nth-child(even) {
    background: #f8f8f8;
}

.status {
    font-weight: bold;
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
    <th>Статус</th>
    <th>Дата</th>
</tr>
"""

    for row in rows:
        html += f"""
<tr>
    <td>{row['id']}</td>
    <td>{row['product']}</td>
    <td>{row['name']}</td>
    <td>{row['phone']}</td>
    <td class="status">{row['status']}</td>
    <td>{row['created_at']}</td>
</tr>
"""

    html += """
</table>

</body>
</html>
"""

    return HTMLResponse(content=html)
