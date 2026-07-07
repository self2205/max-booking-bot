import time
import uuid
import requests

from config import TG_POST_TOKEN

from telegram_poster import send_post

from database import save_product


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None



def get_updates():

    global offset


    params = {
        "timeout": 30
    }


    if offset:

        params["offset"] = offset



    try:

        response = requests.get(

            f"{API_URL}/getUpdates",

            params=params,

            timeout=35

        )


        return response.json()



    except Exception as e:


        print(
            "GET UPDATES ERROR:",
            e,
            flush=True
        )


        return {}





def process_updates():

    global offset


    print(
        "CHECKING TELEGRAM UPDATES",
        flush=True
    )


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



        if not photo:


            print(
                "MESSAGE WITHOUT PHOTO SKIPPED",
                flush=True
            )


            continue





        caption = message.get(
            "caption",
            ""
        )



        product = caption or "Товар"



        file_id = photo[-1]["file_id"]




        print(
            "========== NEW TELEGRAM POST ==========",
            flush=True
        )


        print(
            "PRODUCT:",
            product,
            flush=True
        )


        print(
            "PHOTO:",
            file_id,
            flush=True
        )



        try:



            # создаем ID товара

            product_id = str(
                uuid.uuid4()
            )[:8]




            result = send_post(

                product=product,

                image_url=file_id,

                product_id=product_id

            )



            print(
                "POST RESULT:",
                result,
                flush=True
            )



            # получаем ID сообщения Telegram

            message_id = None



            if result:

                message_id = (
                    result
                    .get("result", {})
                    .get("message_id")
                )



            print(
                "TELEGRAM MESSAGE ID:",
                message_id,
                flush=True
            )





            save_product(

                product_id=product_id,

                product=product,

                image_url=file_id,

                telegram_message_id=message_id

            )



            print(
                "PRODUCT SAVED:",
                product_id,
                flush=True
            )



            print(
                "========================================",
                flush=True
            )





        except Exception as e:



            print(
                "SEND POST ERROR:",
                e,
                flush=True
            )








def start_listener():


    print(
        "STARTING TELEGRAM LISTENER",
        flush=True
    )



    while True:



        try:


            process_updates()



        except Exception as e:



            print(
                "LISTENER ERROR:",
                e,
                flush=True
            )



        time.sleep(2)
