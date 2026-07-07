import requests

from config import TG_TOKEN, TG_CHAT_ID


API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"



def send_booking_to_telegram(
        product,
        name,
        phone,
        image_url=None,
        booking_id=None
):

    text = f"""
🟢 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ

№{booking_id}

📦 {product}

👤 Имя: {name}

📞 Телефон: {phone}
"""


    try:

        if image_url:

            requests.post(
                f"{API_URL}/sendPhoto",
                json={
                    "chat_id": TG_CHAT_ID,
                    "photo": image_url,
                    "caption": text
                },
                timeout=20
            )

        else:

            requests.post(
                f"{API_URL}/sendMessage",
                json={
                    "chat_id": TG_CHAT_ID,
                    "text": text
                },
                timeout=20
            )


        print(
            "TELEGRAM BOOKING SENT",
            flush=True
        )


    except Exception as e:

        print(
            "TELEGRAM NOTIFY ERROR:",
            e,
            flush=True
        )
