import requests

from config import (
    TG_POST_TOKEN,
    TG_CHAT_ID
)


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"



def send_booking_notification(
        booking_id,
        product,
        name,
        phone,
        image_url=None
):

    text = f"""
🟢 НОВАЯ ЗАЯВКА

№{booking_id}

📦 {product}

👤 Имя:
{name}

📞 Телефон:
{phone}
"""


    try:

        if image_url:

            response = requests.post(

                f"{API_URL}/sendPhoto",

                json={
                    "chat_id": TG_CHAT_ID,
                    "photo": image_url,
                    "caption": text
                },

                timeout=20

            )


        else:

            response = requests.post(

                f"{API_URL}/sendMessage",

                json={
                    "chat_id": TG_CHAT_ID,
                    "text": text
                },

                timeout=20

            )


        print(
            "========== SEND BOOKING TO TG =========="
        )

        print(
            response.text
        )

        print(
            "========================================="
        )


        return response.json()



    except Exception as e:

        print(
            "TELEGRAM NOTIFY ERROR:",
            e
        )

        return {}
