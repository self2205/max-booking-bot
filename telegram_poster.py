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
# СОЗДАНИЕ КНОПКИ MAX
# ==================================

def create_max_button(
        product,
        image_url=None
):

    product_id = str(uuid.uuid4())[:8]


    if isinstance(image_url, list):

        db_image = image_url[0]

    else:

        db_image = image_url



    save_product(
        product_id,
        product,
        db_image
    )



    return {

        "inline_keyboard": [

            [

                {
                    "text": "🟢 Забронировать",
                    "url":
                    f"https://max.ru/{MAX_BOT_USERNAME}?start={product_id}"
                }

            ]

        ]

    }





# ==================================
# ПОСТ В КАНАЛ
# ==================================

def send_post(
        product,
        image_url=None
):


    reply_markup = create_max_button(
        product,
        image_url
    )



    try:


        # ==================================
        # АЛЬБОМ
        # ==================================

        if isinstance(image_url, list):


            media = []


            for i, photo in enumerate(image_url):


                item = {

                    "type": "photo",

                    "media": photo

                }


                if i == 0:

                    item["caption"] = product


                media.append(item)



            response = requests.post(

                f"{API_URL}/sendMediaGroup",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "media": media

                },

                timeout=30

            )



            result = response.json()



            print(
                "ALBUM RESULT:",
                result,
                flush=True
            )



            # ==================================
            # ДОБАВЛЯЕМ КНОПКУ К ПЕРВОМУ ФОТО
            # ==================================

            if result.get("ok"):


                first_message_id = result["result"][0]["message_id"]



                edit = requests.post(

                    f"{API_URL}/editMessageReplyMarkup",

                    json={

                        "chat_id": TG_CHANNEL_CHAT_ID,

                        "message_id": first_message_id,

                        "reply_markup": reply_markup

                    },

                    timeout=20

                )



                print(
                    "BUTTON EDIT:",
                    edit.text,
                    flush=True
                )



            return result







        # ==================================
        # ОДНО ФОТО
        # ==================================

        elif image_url:


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





        # ==================================
        # ТЕКСТ
        # ==================================

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
            "POST RESULT:",
            response.text,
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
