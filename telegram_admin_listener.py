import time
import requests


from config import (
    TG_TOKEN,
    ADMIN_IDS
)


from database import (
    get_booking,
    change_status
)


from reply_manager import (
    set_reply_mode,
    get_reply_client,
    clear_reply_mode
)


from max_service import (
    send_message_max
)



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
            "GET UPDATES ERROR:",
            e,
            flush=True
        )


        return {}






# ==========================
# SEND TG MESSAGE
# ==========================

def send_telegram(
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
            e,
            flush=True
        )







# ==========================
# CALLBACK BUTTONS
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


    print(
        "CALLBACK:",
        data,
        flush=True
    )



    if admin_id not in ADMIN_IDS:

        return





    # ======================
    # ОТВЕТИТЬ
    # ======================

    if data.startswith("reply_"):


        booking_id = int(
            data.replace(
                "reply_",
                ""
            )
        )



        booking = get_booking(
            booking_id
        )



        if not booking:


            send_telegram(

                admin_id,

                "❌ Заявка не найдена"

            )


            return




        client_chat_id = booking.get(
            "client_chat_id"
        )



        if not client_chat_id:


            send_telegram(

                admin_id,

                "❌ У клиента нет MAX chat_id"

            )


            return




        set_reply_mode(

            admin_id,

            client_chat_id

        )



        send_telegram(

            admin_id,

            "💬 Режим ответа включен.\n\n"
            "Пишите сообщение — оно уйдет клиенту в MAX."

        )





    # ======================
    # ВЫПОЛНЕНО
    # ======================

    elif data.startswith("done_"):


        booking_id = int(

            data.replace(
                "done_",
                ""
            )

        )


        change_status(
            booking_id
        )


        send_telegram(

            admin_id,

            f"✅ Заявка #{booking_id} изменена"

        )






    # ======================
    # ОТМЕНА
    # ======================

    elif data.startswith("cancel_"):


        booking_id = int(

            data.replace(
                "cancel_",
                ""
            )

        )


        change_status(
            booking_id
        )


        send_telegram(

            admin_id,

            f"❌ Заявка #{booking_id} отменена"

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
            "FULL UPDATE:",
            update,
            flush=True
        )




        # ======================
        # BUTTON
        # ======================

        callback = update.get(
            "callback_query"
        )


        if callback:


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






        # ======================
        # MESSAGE FROM ADMIN
        # ======================


        message = update.get(
            "message"
        )


        if not message:

            continue




        admin_id = message.get(
            "from",
            {}
        ).get(
            "id"
        )



        if admin_id not in ADMIN_IDS:

            continue




        text = message.get(
            "text",
            ""
        )



        print(
            "ADMIN MESSAGE:",
            text,
            flush=True
        )




        client_chat_id = get_reply_client(
            admin_id
        )



        if client_chat_id:


            send_message_max(

                client_chat_id,

                text

            )



            send_telegram(

                admin_id,

                "✅ Сообщение отправлено клиенту"

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
