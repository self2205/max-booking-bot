import time
import requests


from config import (
    TG_TOKEN,
    ADMIN_IDS
)


from telegram_service import (
    send_to_channel,
    handle_admin_commands
)


from reply_manager import (
    set_reply_mode,
    get_reply_client,
    clear_reply_mode
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

        r = requests.get(
            f"{API_URL}/getUpdates",
            params=params,
            timeout=35
        )


        data = r.json()


        print(
            "GET UPDATES:",
            data,
            flush=True
        )


        return data


    except Exception as e:

        print(
            "GET ERROR:",
            e,
            flush=True
        )

        return {}




# ==========================
# SEND TG MESSAGE
# ==========================

def send_tg(
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
            "SEND TG ERROR:",
            e
        )





# ==========================
# CALLBACK
# ==========================

def process_callback(callback):


    data = callback.get(
        "data",
        ""
    )


    admin_id = callback.get(
        "from",
        {}
    ).get(
        "id"
    )



    if admin_id not in ADMIN_IDS:

        return




    if data.startswith("reply_"):


        booking_id = int(
            data.replace(
                "reply_",
                ""
            )
        )


        from database import get_booking


        booking = get_booking(
            booking_id
        )


        if not booking:

            send_tg(
                admin_id,
                "❌ Заявка не найдена"
            )

            return



        client_chat_id = booking["client_chat_id"]



        if not client_chat_id:


            send_tg(

                admin_id,

                "❌ У клиента нет MAX chat_id"

            )

            return



        set_reply_mode(

            admin_id,

            client_chat_id

        )


        send_tg(

            admin_id,

            "💬 Режим ответа клиенту включен.\n\n"
            "Все сообщения будут уходить клиенту в MAX."

        )




    elif data.startswith("done_"):


        from database import change_status


        booking_id = int(
            data.replace(
                "done_",
                ""
            )
        )


        change_status(
            booking_id
        )


    elif data.startswith("cancel_"):


        from database import change_status


        booking_id = int(
            data.replace(
                "cancel_",
                ""
            )
        )


        change_status(
            booking_id
        )





# ==========================
# PROCESS
# ==========================

def process_updates():


    global offset


    data = get_updates()



    for update in data.get(
        "result",
        []
    ):



        offset = update["update_id"] + 1



        # --------------------------
        # BUTTON
        # --------------------------

        callback = update.get(
            "callback_query"
        )


        if callback:


            print(
                "CALLBACK:",
                callback,
                flush=True
            )


            process_callback(
                callback
            )


            requests.post(

                f"{API_URL}/answerCallbackQuery",

                json={

                    "callback_query_id":
                    callback["id"]

                }

            )


            continue





        # --------------------------
        # MESSAGE
        # --------------------------

        message = update.get(
            "message"
        )


        if not message:

            continue



        user_id = message.get(
            "from",
            {}
        ).get(
            "id"
        )


        text = message.get(
            "text",
            ""
        )



        if user_id not in ADMIN_IDS:

            continue




        print(

            "ADMIN MESSAGE:",

            text,

            flush=True

        )



        # если админ в режиме ответа

        client_chat_id = get_reply_client(
            user_id
        )


        if client_chat_id:


            send_message_max(

                client_chat_id,

                text

            )


            print(

                "SEND TO CLIENT:",
                client_chat_id,

                flush=True

            )


            continue





        # обычные команды

        handle_admin_commands(

            message,

            lambda x: send_tg(
                user_id,
                x
            )

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
