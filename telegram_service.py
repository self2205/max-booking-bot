import requests
from config import TG_TOKEN, TG_CHAT_ID
from database import change_status, get_bookings

ADMIN_TG_ID = 441725473


def send_to_telegram(product, name, phone, image_url=None):
    try:

        text = f"""📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

        print("========== TELEGRAM ==========")

        if image_url:

            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"

            response = requests.post(
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

            response = requests.post(
                url,
                data={
                    "chat_id": TG_CHAT_ID,
                    "text": text
                },
                timeout=15
            )

        print("Status:", response.status_code)
        print("Response:", response.text)
        print("==============================")

    except Exception as e:
        print("Telegram error:", e)


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
