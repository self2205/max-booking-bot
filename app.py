from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config import *
from database import init_db, get_bookings
from booking_service import create_booking
from max_service import send_message_max
from states import set_state, get_state, clear_state

app = FastAPI()

# ==========================
# INIT DB
# ==========================
init_db()


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
# WEBHOOK
# ==========================
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("FULL WEBHOOK:", data)

    message = data.get("message", {})
    body = message.get("body", {})
    sender = message.get("sender", {})
    recipient = message.get("recipient", {})

    text = body.get("text", "")
    user_id = sender.get("user_id")

    # ⚡ В MAX ЭТО И ЕСТЬ КЛЮЧ ОТПРАВКИ
    chat_id = recipient.get("chat_id")

    if not user_id or not chat_id:
        return {"ok": True}

    # =========================
    # STATE
    # =========================
    state = get_state(user_id)

    # =========================
    # IMAGE
    # =========================
    image_url = None
    for a in body.get("attachments", []):
        if a.get("type") == "image":
            image_url = a.get("payload", {}).get("url")

    # =========================
    # START
    # =========================
    if text == "/start":
        set_state(user_id, "WAIT_PRODUCT", {})

        send_message_max(chat_id, "👋 Привет!\nЧто хотите забронировать?")
        return {"ok": True}

    # =========================
    # PRODUCT
    # =========================
    if state and state.get("state") == "WAIT_PRODUCT":

        data_state = state.get("data", {})
        data_state["product"] = text
        data_state["image_url"] = image_url

        set_state(user_id, "WAIT_NAME", data_state)

        send_message_max(chat_id, "✍️ Введите ваше имя")
        return {"ok": True}

    # =========================
    # NAME
    # =========================
    if state and state.get("state") == "WAIT_NAME":

        data_state = state.get("data", {})
        data_state["name"] = text

        set_state(user_id, "WAIT_PHONE", data_state)

        send_message_max(chat_id, "📞 Введите телефон")
        return {"ok": True}

    # =========================
    # PHONE
    # =========================
    if state and state.get("state") == "WAIT_PHONE":

        data_state = state.get("data", {})
        data_state["phone"] = text

        booking_id = create_booking(
            product=data_state.get("product"),
            name=data_state.get("name"),
            phone=data_state.get("phone"),
            image_url=data_state.get("image_url")
        )

        clear_state(user_id)

        send_message_max(
            chat_id,
            f"✅ Заявка создана!\nID: {booking_id}"
        )

        return {"ok": True}

    # =========================
    # FALLBACK
    # =========================
    send_message_max(chat_id, "Напишите /start чтобы начать")

    return {"ok": True}


# ==========================
# ADMIN PANEL
# ==========================
@app.get("/admin", response_class=HTMLResponse)
def admin():

    rows = get_bookings()

    html = "<h1>Заявки</h1><table border='1'>"
    html += "<tr><th>ID</th><th>Товар</th><th>Имя</th><th>Телефон</th></tr>"

    for r in rows:
        html += f"<tr><td>{r['id']}</td><td>{r['product']}</td><td>{r['name']}</td><td>{r['phone']}</td></tr>"

    html += "</table>"

    return HTMLResponse(html)
