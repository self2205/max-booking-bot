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
# ПОЛУЧЕНИЕ URL ФОТО
# ==================================

def get_file_url(file_id):

    try:

        response = requests.get(

            f"{API_URL}/getFile",

            params={
                "file_id": file_id
            },

            timeout=15

        )


        data = response.json()


        if not data.get("ok"):

            print(
                "GET FILE ERROR:",
                data,
                flush=True
            )

            return None



        file_path = data["result"]["file_path"]


        url = (
            f"https://api.telegram.org/file/bot"
            f"{TG_POST_TOKEN}/"
            f"{file_path}"
        )


        print(
            "PHOTO URL:",
            url,
            flush=True
        )


        return url



    except Exception as e:

        print(
            "GET FILE EXCEPTION:",
            e,
            flush=True
        )

        return None





# ==================================
# ENCODE PAYLOAD
# ==================================

def encode_payload(data: dict):

    raw = json.dumps(
        data,
        ensure_ascii=False
    )


    encoded = base64.urlsafe_b64encode(
        raw.encode("utf-8")
    ).decode("utf-8")


    return encoded





# ==================================
# КНОПКА MAX
# ==================================

def create_max_button(product, image_url=None):


    product_id = str(uuid.uuid4())[:8]


    save_product(

        product_id,

        product,

        image_url

    )



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


    # если пришёл telegram file_id
    # превращаем его в настоящий URL

    if image_url:

        image_url = get_file_url(
            image_url
        )



    reply_markup = create_max_button(

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




        print(
            "========== POST TO CHANNEL ==========",
            flush=True
        )


        print(
            response.text,
            flush=True
        )


        print(
            "======================================",
            flush=True
        )



        return response.json()



    except Exception as e:


        print(

            "TELEGRAM POST ERROR:",

            e,

            flush=True

        )


        return {}
