import json
import base64
import requests
import uuid

from database import save_product

from config import (
    TG_POST_TOKEN,
    TG_CHANNEL_CHAT_ID,
    MAX_BOT_USERNAME
)



API_URL = (
    f"https://api.telegram.org/bot{TG_POST_TOKEN}"
)




# ==================================
# ENCODE PAYLOAD
# ==================================

def encode_payload(data: dict):

    raw = json.dumps(
        data,
        ensure_ascii=False
    )


    return base64.urlsafe_b64encode(
        raw.encode("utf-8")
    ).decode("utf-8")






# ==================================
# КНОПКА MAX
# ==================================

def create_max_button(
        product_id
):


    max_url = (
        f"https://max.ru/"
        f"{MAX_BOT_USERNAME}"
        f"?start={product_id}"
    )


    return {

        "inline_keyboard": [

            [

                {
                    "text": "🟢 Забронировать",
                    "url": max_url
                }

            ]

        ]

    }







# ==================================
# ОТПРАВКА ПОСТА В КАНАЛ
# ==================================

def send_post(
        product,
        image_url=None
):


    product_id = str(uuid.uuid4())[:8]



    try:



        # ==========================
        # ЕСЛИ ЕСТЬ ФОТО
        # ==========================

        if image_url:


            response = requests.post(

                f"{API_URL}/sendPhoto",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "photo": image_url,

                    "caption": product

                },

                timeout=20

            )



        else:


            response = requests.post(

                f"{API_URL}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": product

                },

                timeout=20

            )





        result = response.json()



        print(
            "========== CHANNEL POST =========="
        )

        print(
            result
        )

        print(
            "=================================="
        )




        if not result.get("ok"):


            return result





        # ==========================
        # ID СООБЩЕНИЯ В КАНАЛЕ
        # ==========================

        message_id = (
            result["result"]["message_id"]
        )



        print(
            "CHANNEL MESSAGE ID:",
            message_id
        )





        # ==========================
        # СОХРАНЯЕМ ТОВАР
        # ==========================

        save_product(

            product_id,

            product,

            image_url,

            message_id

        )





        # ==========================
        # ДОБАВЛЯЕМ КНОПКУ
        # ==========================

        requests.post(

            f"{API_URL}/editMessageReplyMarkup",

            json={

                "chat_id": TG_CHANNEL_CHAT_ID,

                "message_id": message_id,

                "reply_markup":
                    create_max_button(
                        product_id
                    )

            },

            timeout=20

        )




        return result




    except Exception as e:


        print(
            "TELEGRAM POST ERROR:",
            e,
            flush=True
        )


        return {}
