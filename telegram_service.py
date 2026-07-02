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
