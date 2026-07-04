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

    if not user_id:
        return {"ok": True}

    state = get_state(user_id)

    # IMAGE
    image_url = extract_image_from_webhook(message)

    # START
    if text == "/start":

        set_state(user_id, {
            "state": "WAIT_PRODUCT",
            "data": {"image_url": image_url}
        })

        send_message_max(recipient, "👋 Привет!\n\nЧто хотите забронировать?")
        return {"ok": True}

    # PRODUCT
    if state and state["state"] == "WAIT_PRODUCT":

        state["data"]["product"] = text
        state["data"]["image_url"] = image_url

        set_state(user_id, {
            "state": "WAIT_NAME",
            "data": state["data"]
        })

        send_message_max(recipient, "✍️ Введите ваше имя")
        return {"ok": True}

    # NAME
    if state and state["state"] == "WAIT_NAME":

        state["data"]["name"] = text

        set_state(user_id, {
            "state": "WAIT_PHONE",
            "data": state["data"]
        })

        send_message_max(recipient, "📞 Введите телефон")
        return {"ok": True}

    # PHONE
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
            recipient,
            f"✅ Заявка создана!\n\nID: {booking_id}"
        )

        return {"ok": True}

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
