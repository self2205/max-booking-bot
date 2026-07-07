import requests

from config import (
    TG_TOKEN,
    ADMIN_IDS,
    TG_CHANNEL_CHAT_ID
)

from database import (
    change_status,
    get_bookings,
    get_product_by_name
)



API_URL = (
    f"https://api.telegram.org/bot{TG_TOKEN}"
)



# ==================================
# ПОЛУЧЕНИЕ ФОТО ИЗ КАНАЛА
# ==================================

def get_channel_photo(message_id):

    try:

        response = requests.get(

            f"{API_URL}/getChat",

            params={
                "chat_id": TG_CHANNEL_CHAT_ID
            },

            timeout=10

        )


        # фото достаем через forwardMessage
        # поэтому возвращаем message_id

        return message_id


    except Exception as e:

        print(
            "GET CHANNEL PHOTO ERROR:",
            e,
            flush=True
        )

        return None




# ==================================
# ОТПРАВКА ЗАЯВКИ АДМИНАМ
# ==================================

def send_to_telegram(
        product,
        name,
        phone,
        image_url=None
):


    text = f"""
📦 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ


🛍 Товар:
{product}


👤 Имя:
{name}


📞 Телефон:
{phone}
"""



    channel_message_id = None



    # ищем сообщение товара

    try:

        product_data = get_product_by_name(
            product
        )


        if product_data:

            channel_message_id = (
                product_data["channel_message_id"]
            )


    except Exception as e:

        print(
            "PRODUCT SEARCH ERROR:",
            e,
            flush=True
        )




    for admin_id in ADMIN_IDS:


        try:


            # =========================
            # ЕСЛИ ЕСТЬ ФОТО В КАНАЛЕ
            # =========================

            if channel_message_id:


                response = requests.post(

                    f"{API_URL}/forwardMessage",

                    data={

                        "chat_id": admin_id,

                        "from_chat_id": TG_CHANNEL_CHAT_ID,

                        "message_id": channel_message_id

                    },

                    timeout=15

                )


                print(
                    "FORWARD PHOTO:",
                    response.text,
                    flush=True
                )



                # после фото отправляем описание

                requests.post(

                    f"{API_URL}/sendMessage",

                    data={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )


            else:


                response = requests.post(

                    f"{API_URL}/sendMessage",

                    data={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )


                print(
                    "SEND TEXT:",
                    response.text,
                    flush=True
                )




        except Exception as e:


            print(
                "TELEGRAM SEND ERROR:",
                e,
                flush=True
            )





# ==================================
# ПОСТ В КАНАЛ
# ==================================

def send_to_channel(product):


    try:

        response = requests.post(

            f"{API_URL}/sendMessage",

            json={

                "chat_id": TG_CHANNEL_CHAT_ID,

                "text": product

            },

            timeout=15

        )


        print(
            "CHANNEL POST:",
            response.text,
            flush=True
        )


        return response.json()



    except Exception as e:


        print(
            "CHANNEL ERROR:",
            e,
            flush=True
        )




# ==================================
# ADMIN COMMANDS
# ==================================

def handle_admin_commands(message, send_func):


    text = message.get(
        "text",
        ""
    )


    user_id = message.get(
        "from",
        {}
    ).get(
        "id"
    )


    if user_id not in ADMIN_IDS:

        return



    if text.startswith("/status"):


        try:

            booking_id = int(
                text.split()[1]
            )

        except:

            send_func(
                "❌ Используй: /status 12"
            )

            return



        change_status(
            booking_id
        )


        send_func(
            f"✅ Статус заявки #{booking_id} обновлён"
        )



    elif text == "/list":


        rows = get_bookings()


        msg = (
            "📋 Последние заявки\n\n"
        )


        for r in rows[:10]:

            msg += (
                f"#{r['id']} | "
                f"{r['product']} | "
                f"{r['status']}\n"
            )


        send_func(msg)





# ==================================
# ГЕНЕРАТОР ПОСТОВ
# ==================================

def handle_post_generator(message, send_func):


    user_id = message.get(
        "from",
        {}
    ).get(
        "id"
    )


    if user_id not in ADMIN_IDS:

        return False



    text = message.get(
        "text",
        ""
    ).strip()



    if not text or text.startswith("/"):

        return False



    send_to_channel(
        text
    )


    send_func(
        "✅ Пост опубликован"
    )


    return True





# ==================================
# DISPATCHER
# ==================================

def handle_message(message, send_func):


    handle_admin_commands(
        message,
        send_func
    )


    if handle_post_generator(
        message,
        send_func
    ):

        return
