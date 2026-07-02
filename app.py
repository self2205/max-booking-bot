from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import secrets
import requests
import urllib3

from database import init_db, save_booking

app = FastAPI()

# отключаем SSL warning (MAX API)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        text = f"""📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={
                "chat_id": TG_CHAT_ID,
                "text": text
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)


# ==========================
# MAX
# ==========================
MAX_TOKEN = "f9LHodD0cOKUy_Tbz6q5rtrtWCdP8ftMcXbxymfoVF6qNAUQkqI9JcL9earTMlC8jPkdXWhctB1zilcJ0JTC"


def send_message_max(data, text: str):
    try:
        url = "https://platform-api2.max.ru/messages"

        recipient = data.get("message", {}).get("recipient")

        payload = {
            "recipient": recipient,
            "text": text
        }

        headers = {
            "Authorization": MAX_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False,
            timeout=10
        )

        print("MAX STATUS:", response.status_code)
        print("MAX RESPONSE:", response.text)

    except Exception as e:
        print("MAX ERROR:", e)


# ==========================
# AUTH
# ==========================
security = HTTPBasic()

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        secrets.compare_digest(credentials.username, ADMIN_LOGIN) and
        secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    ):
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
    return {"status": "ok", "service": "MAX bot"}


# ==========================
# BOOKING
# ==========================
@app.post("/booking")
def booking(data: Booking):

    save_booking(data.product, data.name, data.phone)
    send_to_telegram(data.product, data.name, data.phone)

    return {"success": True}


# ==========================
# WEBHOOK MAX
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
        send_message_max(data, "Привет 👋\nЯ бот бронирования магазина")

    elif text:
        send_message_max(data, f"Ты написал: {text}")

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
<h2>📋 Заявки</h2>
<table border="1">
<tr>
<th>ID</th>
<th>Товар</th>
<th>Имя</th>
<th>Телефон</th>
<th>Дата</th>
</tr>
"""

    for r in rows:
        html += f"""
<tr>
<td>{r[0]}</td>
<td>{r[1]}</td>
<td>{r[2]}</td>
<td>{r[3]}</td>
<td>{r[4]}</td>
</tr>
"""

    html += "</table>"

    return HTMLResponse(content=html)
