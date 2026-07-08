import time
import requests

from config import (
    TG_TOKEN,
    ADMIN_IDS
)

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



    try:

        response = requests.get(

            f"{API_URL}/getUpdates",

            params=params,

            timeout=35

        )


        result = response.json()


        print(
            "GET UPDATES:",
            result,
            flush=True
        )


        return result


    except Exception as e:


        print(
            "GET UPDATES ERROR:",
            e,
            flush=True
        )


        return {}





# ==========================
# SEND MESSAGE
# ==========================

def send_admin_message(
        chat_id,
        text
):


    try:

        requests.post(

            f"{API_URL}/sendMessage",

            json={

                "chat_id": chat_id,

                "text": text

            },

            timeout=15

        )


    except Exception as e:


        print(
            "SEND MESSAGE ERROR:",
            e,
            flush=True
        )





# ==========================
# PROCESS UPDATES
# ==========================

def process_updates():

    global offset


    data = get_updates()



    for update in data.get(
        "result",
        []
    ):



        offset = update["update_id"] + 1



        print(
            "NEW UPDATE:",
            update,
            flush=True
        )



        # ==========================
        # CALLBACK BUTTON
        # ==========================

        callback = update.get(
            "callback_query"
        )


        if callback:


            print(
                "CALLBACK RECEIVED:",
                callback,
                flush=True
            )


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
                    "HANDLE CALLBACK RESULT:",
                    result,
                    flush=True
                )



                # подтверждаем нажатие кнопки

                requests.post(

                    f"{API_URL}/answerCallbackQuery",

                    json={

                        "callback_query_id":
                        callback["id"]

                    }

                )



                if isinstance(result, dict):


                    if result.get(
                        "action"
                    ) == "reply":


                        send_admin_message(

                            user_id,

                            "✅ Клиент найден.\n"
                            "Chat ID: "
                            + str(
                                result["chat_id"]
                            )

                        )


            continue





        # ==========================
        # MESSAGE
        # ==========================

        message = update.get(
            "message"
        )


        if message:


            print(
                "MESSAGE RECEIVED:",
                message,
                flush=True
            )







# ==========================
# START
# ==========================

def start_admin_listener():


    print(
        "🔥 ADMIN LISTENER STARTED",
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
