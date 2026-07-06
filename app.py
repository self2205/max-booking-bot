from max_service import get_max_message, extract_image
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

import secrets
import requests
import urllib.parse

from config import *
from database import init_db, get_bookings, change_status
from booking_service import create_booking
from max_service import send_message_max
from states import get_state, set_state, clear_state

app = FastAPI()

init_db()

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


class Booking(BaseModel):
    product: str
    name: str
    phone: str


@app.get("/")
def root():
    return {"status": "ok", "service": "MAX Booking Bot"}


@app.post("/booking")
def booking(data: Booking):

    booking_id = create_booking(
        product=data.product,
        name=data.name,
        phone=data.phone
    )

    return {"success": True, "booking_id": booking_id}


# ==========================
# 🔥 PAGE ДЛЯ КНОПКИ
# ==========================
@app.get("/book")
def book_page(product: str = ""):

    safe_product = urllib.parse.quote(product)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Бронирование</title>
    </head>

    <body style="font-family: Arial; text-align:center; padding-top:80px;">

        <h2>📦 Бронирование товара</h2>

        <h3>{product}</h3>

        <p>Нажмите кнопку ниже — вы перейдёте в MAX для оформления брони</p>

        <a href="https://max-booking-bot-k3dx.onrender.com/book?product={safe_product}"
           style="display:inline-block;padding:15px 25px;background:green;color:white;
           text-decoration:none;border-radius:10px;font-size:18px;">
           🟢 Забронировать в MAX
        </a>

    </body>
    </html>
    """

    return HTMLResponse(content=html)


# ==========================
# MAX WEBHOOK
# ==========================
@app.post("/webhook")
async def webhook(request: Request):

    import json, base64

    data = await request.json()

    print("\n========== MAX WEBHOOK ==========")
    print(data)
    print("=================================\n")

    # ==========================
    # START (кнопка из Telegram)
    # ==========================
    if data.get("update_type") == "bot_started":

        user_id = data.get("user_id")
        chat_id = data.get("chat_id")
        payload = data.get("payload", "")

        product = None
        photo = None

        try:
            decoded = base64.urlsafe_b64decode(payload).decode()
            obj = json.loads(decoded)

            product = obj.get("product")
            photo = obj.get("photo")

        except Exception as e:
            print("START decode error:", e)

        if product:

            set_state(user_id, "WAIT_NAME", {
                "product": product,
                "photo": photo
            })

            send_message_max(
                chat_id,
                f"🟢 Бронирование\n\n📦 {product}\n\n✍️ Введите ваше имя"
            )

        else:

            set_state(user_id, "WAIT_PRODUCT", {})

            send_message_max(
                chat_id,
                "👋 Привет!\n\nЧто хотите забронировать?"
            )

        return {"ok": True}

    # ==========================
    # MESSAGE
    # ==========================
    if data.get("update_type") != "message_created":
        return {"ok": True}

    message = data.get("message", {})

    chat_id = message.get("recipient", {}).get("chat_id")
    user_id = message.get("sender", {}).get("user_id")

    body = message.get("body", {})
    text = body.get("text", "")

    if not chat_id:
        return {"ok": True}

    state = get_state(user_id)

    # ==========================
    # STEP PRODUCT
    # ==========================
    if state and state["state"] == "WAIT_PRODUCT":
        state["data"]["product"] = text
        set_state(user_id, "WAIT_NAME", state["data"])

        send_message_max(chat_id, "✍️ Введите ваше имя")
        return {"ok": True}

    # ==========================
    # STEP NAME
    # ==========================
    if state and state["state"] == "WAIT_NAME":
        state["data"]["name"] = text
        set_state(user_id, "WAIT_PHONE", state["data"])

        send_message_max(chat_id, "📞 Введите телефон")
        return {"ok": True}

    # ==========================
    # STEP PHONE
    # ==========================
    if state and state["state"] == "WAIT_PHONE":
        state["data"]["phone"] = text

        create_booking(
            product=state["data"].get("product"),
            name=state["data"].get("name"),
            phone=state["data"].get("phone"),
            image_url=state["data"].get("photo")
        )

        clear_state(user_id)

        send_message_max(chat_id, "✅ Заявка создана!")

        return {"ok": True}

    return {"ok": True}

# ==========================
# TELEGRAM WEBHOOK (FIXED)
# ==========================
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    text = message.get("text") or message.get("caption") or ""

    photo_url = None

    # 📸 ВАЖНО: получаем реальный URL фото (не file_id)
    if message.get("photo"):
        file_id = message["photo"][-1]["file_id"]

        file_info = requests.get(
            f"https://api.telegram.org/bot{TG_TOKEN}/getFile",
            params={"file_id": file_id}
        ).json()

        file_path = file_info["result"]["file_path"]

        photo_url = f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}"

    if not text and not photo_url:
        return {"ok": True}

    product = text.strip() if text else "Товар"

    # ==========================
    # MAX start payload (кодируем всё)
    # ==========================
    import json, base64

    payload_data = {
        "product": product,
        "photo": photo_url
    }

    encoded = base64.urlsafe_b64encode(
        json.dumps(payload_data, ensure_ascii=False).encode()
    ).decode()

    product_url = f"https://max.ru/se13456903_bot?start={encoded}"

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "🟢 Забронировать",
                    "url": product_url
                }
            ]
        ]
    }

    try:
        if photo_url:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                json={
                    "chat_id": TG_CHANNEL_CHAT_ID,
                    "photo": photo_url,
                    "caption": f"📦 {product}",
                    "reply_markup": reply_markup
                },
                timeout=10
            )
        else:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHANNEL_CHAT_ID,
                    "text": f"📦 {product}",
                    "reply_markup": reply_markup
                },
                timeout=10
            )

    except Exception as e:
        print("TELEGRAM ERROR:", e)

    return {"ok": True}
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
    vertical-align: middle;
}

tr:nth-child(even) {
    background: #f8f8f8;
}

.status {
    font-weight: bold;
}

img {
    border-radius: 6px;
}

</style>

</head>

<body>

<h2>📋 Заявки магазина</h2>

<table>

<tr>
    <th>ID</th>
    <th>Фото</th>
    <th>Товар</th>
    <th>Имя</th>
    <th>Телефон</th>
    <th>Статус</th>
    <th>Дата</th>
</tr>
"""

    for row in rows:

        photo = "—"

        if row["image_url"]:
            photo = f"""
            <a href="{row['image_url']}" target="_blank">
                <img src="{row['image_url']}" width="90">
            </a>
            """

        html += f"""
<tr>
    <td>{row['id']}</td>
    <td>{photo}</td>
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

    return HTMLResponse(content=html)
