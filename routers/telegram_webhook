import requests

from fastapi import APIRouter, Request

from config import (
    TG_TOKEN,
    TG_CHANNEL_CHAT_ID
)


router = APIRouter()



# ==========================
# TELEGRAM WEBHOOK
# ==========================

@router.post("/telegram-webhook")
async def telegram_webhook(request: Request):


    data = await request.json()


    print("\n========== TELEGRAM WEBHOOK ==========")
    print(data)
    print("======================================\n")



    message = data.get(
        "message"
    )


    if not message:

        return {
            "ok": True
        }



    text = message.get(
        "text",
        ""
    )


    caption = message.get(
        "caption",
        ""
    )


    photo = message.get(
        "photo"
    )



    product = caption or text



    if not product:

        product = "Товар"



    image_url = None



    # ==========================
    # ПОЛУЧАЕМ ФОТО
    # ==========================

    if photo:

        try:

            file_id = photo[-1]["file_id"]


            response = requests.get(

                f"https://api.telegram.org/bot{TG_TOKEN}/getFile",

                params={
                    "file_id": file_id
                },

                timeout=10

            )


            result = response.json()


            file_path = result["result"]["file_path"]


            image_url = (
                f"https://api.telegram.org/file/"
                f"bot{TG_TOKEN}/{file_path}"
            )


        except Exception as e:

            print(
                "PHOTO ERROR:",
                e
            )



    # ==========================
    # ТЕСТОВАЯ ОТПРАВКА
    # ==========================

    try:


        if image_url:


            requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "photo": image_url,

                    "caption": product

                },

                timeout=15

            )


        else:


            requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": product

                },

                timeout=15

            )


    except Exception as e:

        print(
            "POST ERROR:",
            e
        )



    return {
        "ok": True
    }
