from max_service import get_max_message, extract_image
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

import secrets
import requests
import urllib.parse
import json
import base64

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
# MAX WEBHOOK (FINAL FIX)
# ==========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("\n========== MAX WEBHOOK ==========")
    print(data)
    print("=================================\n")

    update_type = data.get("update_type")

    # ==========================
    # BOT STARTED
    # ==========================
    if update_type == "bot_started":

        user_id = data.get("user_id")
        chat_id = data.get("chat_id")
        payload = data.get("payload", "")

        print("PAYLOAD:", payload)

        product = None

        # ==========================
        # FIXED PARSER (100%)
        # ==========================
        if payload:

            # убираем product_
            if payload.startswith("product_"):
                product = payload.replace("product_", "", 1).strip()

            else:
                product = payload.strip()

        if product:

            set_state(user_id, "WAIT_NAME", {
                "product": product
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
    # MESSAGE FLOW
    # ==========================
    if update_type != "message_created":
        return {"ok": True}

    message = data.get("message", {})

    chat_id = message.get("recipient", {}).get("chat_id")
    user_id = message.get("sender", {}).get("user_id")

    body = message.get("body", {})
    text = body.get("text", "")

    if not chat_id:
        return {"ok": True}

    state = get_state(user_id)

    if text == "/start":
        set_state(user_id, "WAIT_PRODUCT", {})
        send_message_max(chat_id, "👋 Привет!\n\nЧто хотите забронировать?")
        return {"ok": True}

    if state and state["state"] == "WAIT_PRODUCT":
        state["data"]["product"] = text
        set_state(user_id, "WAIT_NAME", state["data"])
        send_message_max(chat_id, "✍️ Введите ваше имя")
        return {"ok": True}

    if state and state["state"] == "WAIT_NAME":
        state["data"]["name"] = text
        set_state(user_id, "WAIT_PHONE", state["data"])
        send_message_max(chat_id, "📞 Введите телефон")
        return {"ok": True}

    if state and state["state"] == "WAIT_PHONE":
        state["data"]["phone"] = text

        booking_id = create_booking(
            product=state["data"].get("product"),
            name=state["data"].get("name"),
            phone=state["data"].get("phone"),
            image_url=state["data"].get("image_url")
        )

        clear_state(user_id)

        send_message_max(
            chat_id,
            f"✅ Заявка создана!\nID: {booking_id}"
        )

        return {"ok": True}

    return {"ok": True}
# ==========================
# TELEGRAM WEBHOOK (FINAL FIX)
# ==========================
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):

    data = await request.json()

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    text = message.get("text") or ""
    caption = message.get("caption") or ""

    photo = message.get("photo")

    # ==========================
    # FIX: full product
    # ==========================
    product = (caption if caption else text).strip()

    if not product:
        product = "Товар"

    # ==========================
    # MAX LINK SAFE
    # ==========================
    product_url = f"https://max.ru/se13456903_bot?start=product_{urllib.parse.quote(product)}"

    reply_markup = json.dumps({
        "inline_keyboard": [
            [
                {
                    "text": "🟢 Забронировать",
                    "url": product_url
                }
            ]
        ]
    })

    try:

        # ==========================
        # PHOTO FIX (REAL SAFE)
        # ==========================
        if photo:

            file_id = photo[-1]["file_id"]

            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                data={
                    "chat_id": TG_CHANNEL_CHAT_ID,
                    "photo": file_id,
                    "caption": f"📦 {product}",
                    "reply_markup": reply_markup
                },
                timeout=15
            )

        else:

            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": TG_CHANNEL_CHAT_ID,
                    "text": f"📦 {product}",
                    "reply_markup": reply_markup
                },
                timeout=15
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
