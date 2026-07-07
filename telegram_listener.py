import time
import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None


# ==========================
# GET TELEGRAM UPDATES
# ==========================

def get_updates():

    global offset


    params = {
        "timeout": 30
    }


    if offset:

        params["offset"] = offset



    response = requests.get(

        f"{API_URL}/getUpdates",

        params=params,

        timeout=35

    )


    return response.json()



# ==========================
# PROCESS MESSAGES
# ==========================

def process_updates():

    global offset


    data = get_updates()



    for update in data.get(
        "result",
        []
    ):


        offset = update["update_id"] + 1



        message = update.get(
            "message"
        )


        if not message:

            continue



        photo = message.get(
            "photo"
        )


        # пропускаем сообщения без фото

        if not photo:

            continue



        caption = message.get(
            "caption",
            ""
        )



        product = caption or "Товар"



        file_id = photo[-1].get(
            "file_id"
        )



        if not file_id:

            continue



        print(
            "========== NEW TELEGRAM POST =========="
        )


        print(
            "PRODUCT:",
            product
        )


        print(
            "PHOTO:",
            file_id
        )


        print(
            "========================================"
        )



        send_post(

            product=product,

            image_url=file_id

        )



# ==========================
# BACKGROUND WORKER
# ==========================

def start_listener():

    print(
        "TELEGRAM LISTENER STARTED"
    )


    while True:


        try:

            process_updates()


        except Exception as e:


            print(
                "TELEGRAM LISTENER ERROR:",
                e
            )



        time.sleep(2)
