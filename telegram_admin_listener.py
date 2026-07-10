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
    get_reply_client
)


from max_service import (
    send_message_max
)



API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"


offset = None

processed_callbacks = []

listener_running = False



# ==========================
# GET UPDATES
# ==========================

def get_updates():

    global offset


    params = {

        "timeout": 30,

        "allowed_updates": [
            "message",
            "callback_query"
        ]

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
# SEND TELEGRAM MESSAGE
# ==========================

def send_telegram(
        chat_id,
        text,
        buttons=None
):

    payload = {

        "chat_id": chat_id,

        "text": text

    }


    if buttons:

        payload["reply_markup"] = {

            "inline_keyboard": buttons

        }


    try:

        requests.post(

            f"{API_URL}/sendMessage",

            json=payload,

            timeout=15

        )


    except Exception as e:


        print(
            "SEND TG ERROR:",
            e,
            flush=True
        )



# ==========================
# SEND MESSAGE ALL ADMINS
# ==========================

def notify_all_admins(text):

    for admin in ADMIN_IDS:

        send_telegram(
            admin,
            text
        )

# ==========================
# CALLBACK BUTTON
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


    admin_name = callback.get(
        "from",
        {}
    ).get(
        "first_name",
        "Менеджер"
    )


    print(
        "CALLBACK:",
        data,
        flush=True
    )



    # ==========================
    # ЗАЩИТА ОТ ДВОЙНОГО НАЖАТИЯ
    # ==========================

    callback_id = callback.get(
        "id"
    )


    if callback_id in processed_callbacks:

        print(
            "⚠️ DUPLICATE CALLBACK IGNORED:",
            callback_id,
            flush=True
        )

        return



    processed_callbacks.append(
        callback_id
    )


    # оставляем только последние 1000 кнопок

    if len(processed_callbacks) > 1000:

        processed_callbacks.pop(0)



    # ==========================
    # ПРОВЕРКА АДМИНА
    # ==========================

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
            "Пишите сообщение — оно уйдет клиенту."

        )


        return







    # ======================
    # ВЫПОЛНЕНО
    # ======================

    if data.startswith("done_"):


        booking_id = int(

            data.replace(
                "done_",
                ""
            )

        )


        booking = get_booking(
            booking_id
        )


        change_status(
            booking_id
        )


        if booking:


            product_name = booking.get(
                "product",
                "Не указан"
            )


            client_chat_id = booking.get(
                "client_chat_id"
            )


            if client_chat_id:


                send_message_max(

                    client_chat_id,

                    f"✅ Ваш заказ забронирован!\n\n"
                    f"📦 Товар:\n{product_name}\n\n"
                    "Товар подготовлен и ожидает вас.\n\n"
                    "Вы можете забрать его в магазине с 9:00 до 19:00\n\n"
                    "Если товар не будет выкуплен в течение 2 дней, бронирование отменится"

                )


        else:

            product_name = "Не указан"



        notify_all_admins(

            f"✅ Заявка #{booking_id} выполнена.\n\n"
            f"📦 Товар:\n{product_name}\n\n"
            f"👤 Сотрудник: {admin_name}\n"
            "📩 Клиент получил уведомление."

        )


        return

    # ======================
    # ОТМЕНА
    # ======================

    if data.startswith("cancel_"):


        booking_id = int(

            data.replace(
                "cancel_",
                ""
            )

        )


        booking = get_booking(
            booking_id
        )


        change_status(
            booking_id
        )


        if booking:


            product_name = booking.get(
                "product",
                "Не указан"
            )


            client_chat_id = booking.get(
                "client_chat_id"
            )


            if client_chat_id:


                send_message_max(

                    client_chat_id,

                    f"❌ Ваше бронирование отменено.\n\n"
                    f"📦 Товар:\n{product_name}\n\n"
                    "Данного товара нет в наличии, "
                    "либо он уже забронирован другим клиентом.\n\n"
                    "Кнока для связи с менеджером больше не активна."

                )


        else:

            product_name = "Не указан"



        notify_all_admins(

            f"❌ Заявка #{booking_id} отменена.\n\n"
            f"📦 Товар:\n{product_name}\n\n"
            f"👤 Сотрудник: {admin_name}\n"
            "📩 Клиент получил уведомление."

        )


        return


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
        # CALLBACK
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

                },

                timeout=10

            )


            continue






        # ======================
        # MESSAGE
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
# START LISTENER
# ==========================

def start_admin_listener():

    global listener_running


    if listener_running:

        print(
            "⚠️ ADMIN LISTENER ALREADY RUNNING",
            flush=True
        )

        return



    listener_running = True



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
