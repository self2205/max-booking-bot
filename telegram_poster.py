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


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"



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
        product,
        image_url=None
):

    product_id = str(uuid.uuid4())[:8]


    # пока сохраняем без message_id
    save_product(
        product_id,
        product,
        image_url,
        None
    )


    max_url = (
        f"https://max.ru/"
        f"{MAX_BOT_USERNAME}"
        f"?start={product_id}"
    )


    return product_id, {


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


    product_id, reply_markup = create_max_button(
        product,
        image_url
    )



    try:


        if image_url:


            response = requests.post(

                f"{API_URL}/sendPhoto",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "photo": image_url,

                    "caption": product,

                    "reply_markup": reply_markup

                },

                timeout=20

            )


        else:


            response = requests.post(

                f"{API_URL}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": product,

                    "reply_markup": reply_markup

                },

                timeout=20

            )




        data = response.json()



        print(
            "========== POST TO CHANNEL =========="
        )

        print(
            data
        )

        print(
            "======================================"
        )



        # ==========================
        # СОХРАНЯЕМ MESSAGE ID
        # ==========================

        if data.get("ok"):


            message_id = data["result"]["message_id"]


            save_product(

                product_id,

                product,

                image_url,

                message_id

            )


            print(
                "CHANNEL MESSAGE ID:",
                message_id
            )



        return data



    except Exception as e:


        print(
            "TELEGRAM POST ERROR:",
            e
        )


        return {}
