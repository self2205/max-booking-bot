import time
import requests

from config import (
    TG_TOKEN,
    ADMIN_IDS
)

from telegram_service import handle_callback

from reply_manager import (
    set_reply_mode,
    get_reply_client
)

from max_service import send_message_max



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
# SEND MESSAGE ADMIN
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
            "SEND ADMIN ERROR:",
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



            admin_id = callback.get(
                "from",
                {}
            ).get(
                "id"
            )



            if admin_id in ADMIN_IDS:



                result = handle_callback(
                    callback
                )



                print(
                    "CALLBACK RESULT:",
                    result,
                    flush=True
                )



                requests.post(

                    f"{API_URL}/answerCallbackQuery",

                    json={

                        "callback_query_id":
                        callback["id"]

                    },

                    timeout=10

                )





                # ==========================
                # ВКЛЮЧАЕМ РЕЖИМ ОТВЕТА
                # ==========================

                if isinstance(result, dict):


                    if result.get(
                        "action"
                    ) == "reply":



                        client_chat_id = result.get(
                            "chat_id"
                        )



                        if client_chat_id:



                            set_reply_mode(

                                admin_id,

                                client_chat_id

                            )



                            send_admin_message(

                                admin_id,

                                "💬 Режим ответа включён.\n\n"
                                "Теперь отправьте сообщение клиенту."

                            )



                        else:



                            send_admin_message(

                                admin_id,

                                "❌ У клиента нет MAX chat_id"

                            )



            continue







        # ==========================
        # MESSAGE FROM ADMIN
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



            admin_id = message.get(
                "from",
                {}
            ).get(
                "id"
            )



            text = message.get(
                "text",
                ""
            )



            if not text:

                continue



            if admin_id not in ADMIN_IDS:

                continue






            # ==========================
            # ПРОВЕРЯЕМ РЕЖИМ ОТВЕТА
            # ==========================

            client_chat_id = get_reply_client(

                admin_id

            )



            if client_chat_id:



                print(

                    "SENDING TO MAX CLIENT:",

                    client_chat_id,

                    flush=True

                )



                send_message_max(

                    client_chat_id,

                    text

                )



                send_admin_message(

                    admin_id,

                    "✅ Сообщение отправлено клиенту"

                )



                continue







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
