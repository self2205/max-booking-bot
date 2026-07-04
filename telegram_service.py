import requests
from config import TG_TOKEN, TG_CHAT_ID


def send_to_telegram(product, name, phone, image_url=None):

    text = f"""📦 НОВАЯ ЗАЯВКА

🛍 Товар: {product}
👤 Имя: {name}
📞 Телефон: {phone}
"""

    try:
        # =========================
        # 📸 ЕСЛИ ЕСТЬ КАРТИНКА
        # =========================
        if image_url:
            # скачиваем картинку с MAX
            img = requests.get(image_url, timeout=10)
            img.raise_for_status()

            # отправляем в Telegram как файл
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                data={
                    "chat_id": TG_CHAT_ID,
                    "caption": text
                },
                files={
                    "photo": img.content
                },
                timeout=10
            )

            print("📸 Фото отправлено в Telegram")
            return

        # =========================
        # 📝 если картинки нет
        # =========================
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
