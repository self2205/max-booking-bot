import time
import requests

from config import TG_TOKEN, ADMIN_IDS
from telegram_service import handle_callback


API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"


offset = None



# ==========================
# GET UPDATES
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
# PROCESS UPDATES
# ==========================

def process_updates():

    global offset


    data = get_updates()



    for update in data.get("result", []):


        offset = update["update_id"] + 1



        # ==========================
        # КНОПКИ
        # ==========================

        callback = update.get(
            "callback_query"
        )


        if callback:


            user_id = callback.get(
                "from",
                {}
            ).get(
                "id"
            )


            if user_id in ADMIN_IDS:


                result = handle_callback(
                    callback
                )


                print(
                    "CALLBACK RESULT:",
                    result,
                    flush=True
                )



            continue





        # ==========================
        # СООБЩЕНИЯ
        # ==========================

        message = update.get(
            "message"
        )


        if not message:

            continue



        print(
            "ADMIN MESSAGE:",
            message,
            flush=True
        )





# ==========================
# START
# ==========================

def start_admin_listener():

    print(
        "ADMIN LISTENER STARTED",
        flush=True
    )


    while True:


        try:

            process_updates()


        except Exception as e:


            print(
                "ADMIN LISTENER ERROR:",
                e,
                flush=True
            )



        time.sleep(2)
