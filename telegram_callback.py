import requests

from config import TG_TOKEN
from database import get_booking
from max_service import send_message_max


API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"



def handle_callback_query(callback):


    callback_id = callback.get(
        "id"
    )


    data = callback.get(
        "data",
        ""
    )


    if not data.startswith("reply_"):

        return



    booking_id = int(
        data.replace(
            "reply_",
            ""
        )
    )



    booking = get_booking(
        booking_id
    )



    if not booking:

        return



    client_chat_id = booking["client_chat_id"]



    if not client_chat_id:

        return



    send_message_max(

        client_chat_id,

        f"""
💬 Менеджер отвечает по вашей заявке:

📦 {booking['product']}

Введите ваш вопрос или уточнение.
"""

    )



    requests.post(

        f"{API_URL}/answerCallbackQuery",

        json={

            "callback_query_id": callback_id,

            "text": "Открыт чат с клиентом"

        }

    )
