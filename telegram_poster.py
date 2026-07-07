import requests

from config import (
    TG_POST_TOKEN,
    TG_CHANNEL_CHAT_ID,
    MAX_BOT_USERNAME
)


API_URL = (
    f"https://api.telegram.org/bot{TG_POST_TOKEN}"
)


# ==========================
# СОЗДАНИЕ КНОПКИ MAX
# ==========================

def create_max_button(product, image_url=None):

    import base64
    import json


    payload = {

        "product": product,

        "image_url": image_url

    }


    encoded = base64.urlsafe_b64encode(

        json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

    ).decode("utf-8")



    url = (

        f"https://max.ru/"
        f"{MAX_BOT_USERNAME}"
        f"?start={encoded}"

    )



    return {

        "inline_keyboard": [

            [

                {

                    "text": "🟢 Забронировать",

                    "url": url

                }

            ]

        ]

    }



# ==========================
# ОТПРАВКА ПОСТА В КАНАЛ
# ==========================

def send_post(
        product,
        image_url=None
):


    reply_markup = create_max_button(
        product,
        image_url
    )


    try:


        if image_url:


            r = requests.post(

                f"{API_URL}/sendPhoto",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "photo": image_url,

                    "caption": f"📦 {product}",

                    "reply_markup": reply_markup

                },

                timeout=15

            )


        else:


            r = requests.post(

                f"{API_URL}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": f"📦 {product}",

                    "reply_markup": reply_markup

                },

                timeout=15

            )



        print(
            "POST RESULT:",
            r.text
        )


        return r.json()



    except Exception as e:


        print(
            "POST ERROR:",
            e
        )

        return {}
