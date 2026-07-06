import requests
import urllib.parse
import re

from config import TG_TOKEN, TG_CHAT_ID, TG_CHANNEL_CHAT_ID
from database import change_status, get_bookings

ADMIN_TG_ID = 441725473

FASTAPI_URL = "https://max-booking-bot-k3dx.onrender.com/webhook/book"


# ==========================
# ОЧИСТКА ТОВАРА
# ==========================
def clean_product(text: str) -> str:
    text = re.sub(r"[^\w\sа-яА-ЯёЁ0-9\-\+\.\,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:80]


def build_product_url(text: str):
    product = clean_product(text)
    return f"{FASTAPI_URL}?product={urllib.parse.quote(product)}"


# ==========================
# ОТПРАВКА В КАНАЛ (FIXED)
# ==========================
def send_to_channel(product: str):

    product = clean_product(product)
    url = build_product_url(product)

    payload = {
        "chat_id": TG_CHANNEL_CHAT_ID,
        "text": f"📦 {product}",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "🟢 Забронировать",
                        "url": url
                    }
                ]
            ]
        }
    }

    resp = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json=payload,
        timeout=15
    )

    print("CHANNEL RESPONSE:", resp.status_code, resp.text)
    return resp.json()


# ==========================
# TELEGRAM SEND (ЗАЯВКИ MAX → ТЕБЕ)
# ==========================
def send_to_telegram(product, name, phone, image_url=None):
    try:

        text = f"""📦 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

        if image_url:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"

            requests.post(
                url,
                data={
                    "chat_id": TG_CHAT_ID,
                    "photo": image_url,
                    "caption": text
                },
                timeout=15
            )

        else:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

            requests.post(
                url,
                data={
                    "chat_id": TG_CHAT_ID,
                    "text": text
                },
                timeout=15
            )

    except Exception as e:
        print("Telegram error:", e)


# ==========================
# POST GENERATOR
# ==========================
def handle_post_generator(message, send_func):

    text = message.get("text", "").strip()

    if not text or text.startswith("/"):
        return False

    product = clean_product(text)

    # 👉 ОТПРАВКА В КАНАЛ
    send_to_channel(product)

    # (опционально) ответ в бота
    send_func(f"📦 Опубликовано: {product}")

    return True


# ==========================
# ADMIN COMMANDS
# ==========================
def handle_admin_commands(message, send_func):

    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    if user_id != ADMIN_TG_ID:
        return

    if text.startswith("/status"):

        try:
            booking_id = int(text.split()[1])
        except:
            send_func("❌ Используй: /status 12")
            return

        change_status(booking_id)
        send_func(f"✅ Статус заявки #{booking_id} обновлён")
        return

    if text == "/list":

        rows = get_bookings()
        msg = "📋 Заявки:\n\n"

        for r in rows[:10]:
            msg += f"#{r['id']} | {r['product']} | {r['status']}\n"

        send_func(msg)
        return


# ==========================
# MAIN DISPATCHER
# ==========================
def handle_message(message, send_func):

    handle_admin_commands(message, send_func)

    if handle_post_generator(message, send_func):
        return
