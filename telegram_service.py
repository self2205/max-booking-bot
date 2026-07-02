import requests

from config import TG_TOKEN, TG_CHAT_ID


def send_to_telegram(product, name, phone):
    """
    Отправка новой заявки в Telegram
    """

    try:
        text = f"""📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": TG_CHAT_ID,
                "text": text
            },
            timeout=10
        )

        print("========== TELEGRAM ==========")
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("==============================")

    except Exception as e:
        print("Telegram error:", e)

from database import change_status, get_bookings

ADMIN_TG_ID = 441725473  # твой Telegram ID


def handle_admin_commands(message, send_func):
    """
    Обработка команд из Telegram:
    /status 12
    /list
    """

    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    # защита — только ты можешь управлять
    if user_id != ADMIN_TG_ID:
        return

    # ----------------------
    # смена статуса
    # ----------------------
    if text.startswith("/status"):
        try:
            booking_id = int(text.split()[1])
        except:
            send_func("❌ Используй: /status 12")
            return

        change_status(booking_id)
        send_func(f"✅ Статус заявки #{booking_id} обновлён")
        return

    # ----------------------
    # список заявок
    # ----------------------
    if text == "/list":
        rows = get_bookings()

        msg = "📋 Заявки:\n\n"

        for r in rows[:10]:
            msg += f"#{r['id']} | {r['product']} | {r['status']}\n"

        send_func(msg)
