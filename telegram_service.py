import requests
from config import TG_TOKEN, TG_CHAT_ID


def send_to_telegram(product, name, phone, image_url=None):

    text = f"""📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

    # =========================
    # 📸 ЕСЛИ ЕСТЬ КАРТИНКА
    # =========================
    if image_url:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
            data={
                "chat_id": TG_CHAT_ID,
                "photo": image_url,
                "caption": text
            },
            timeout=10
        )
        return

    # =========================
    # ТЕКСТОВЫЙ ВАРИАНТ
    # =========================
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data={
            "chat_id": TG_CHAT_ID,
            "text": text
        },
        timeout=10
    )

# =========================
# АДМИН КОМАНДЫ В TELEGRAM
# =========================
def handle_admin_commands(message, send_func):
    """
    /status 12
    /list
    """

    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    # защита
    if user_id != ADMIN_TG_ID:
        return

    # ----------------------
    # /status ID
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
    # /list
    # ----------------------
    if text == "/list":
        rows = get_bookings()

        msg = "📋 Заявки:\n\n"

        for r in rows[:10]:
            msg += f"#{r[0]} | {r[1]} | {r[4]}\n"

        send_func(msg)
