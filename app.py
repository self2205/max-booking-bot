from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import secrets
import requests

from database import init_db, save_booking

app = FastAPI()

# ==========================
# INIT DB
# ==========================
init_db()

# ==========================
# TELEGRAM
# ==========================
TG_TOKEN = "8977629291:AAFZLDW_YHDYj8ZB8KePSHQVBgyRaxbmh-Y"
TG_CHAT_ID = "441725473"


def send_to_telegram(product, name, phone):
    try:
        text = f"""
📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": text
        })

    except Exception as e:
        print("Telegram error:", e)


# ==========================
# ADMIN AUTH
# ==========================
security = HTTPBasic()

ADMIN_LOGIN = "moysklad"
ADMIN_PASSWORD = "pass1973"


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    login_ok = secrets.compare_digest(credentials.username, ADMIN_LOGIN)
    password_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (login_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
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

    save_booking(
        data.product,
        data.name,
        data.phone
    )

    send_to_telegram(data.product, data.name, data.phone)

    print("\n========== НОВАЯ ЗАЯВКА ==========")
    print(f"Товар: {data.product}")
    print(f"Имя: {data.name}")
    print(f"Телефон: {data.phone}")
    print("=================================\n")

    return {"success": True}


# ==========================
# WEBHOOK
# ==========================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("========== СОБЫТИЕ MAX ==========")
    print(data)
    print("=================================")

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
<title>Заявки</title>

<style>
body{
    font-family:Arial,sans-serif;
    background:#f4f4f4;
    padding:40px;
}

h2{margin-bottom:20px;}

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
    padding:12px;
    border:1px solid #ddd;
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
