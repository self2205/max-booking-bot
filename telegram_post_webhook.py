import time
import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None


def get_updates():

    global offset


    params = {
        "timeout": 30
    }


    if offset:

        params["offset"] = offset



    r = requests.get(

        f"{API_URL}/getUpdates",

        params=params,

        timeout=35

    )


    return r.json()



def process_updates():

    global offset


    data = get_updates()


    for update in data.get("result", []):


        offset = update["update_id"] + 1



        message = update.get(
            "message"
        )


        if not message:
            continue



        photo = message.get(
            "photo"
        )


        if not photo:

            continue



        caption = message.get(
            "caption",
            ""
        )


        product = caption or "Товар"



        file_id = photo[-1]["file_id"]



        print(
            "NEW POST:",
            product
        )



        send_post(

            product=product,

            image_url=file_id

        )



while True:


    try:

        process_updates()


    except Exception as e:

        print(
            "ERROR:",
            e
        )


    time.sleep(2)
