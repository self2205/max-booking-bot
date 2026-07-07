import requests

from config import (
    TG_TOKEN,
    ADMIN_IDS,
    TG_CHANNEL_CHAT_ID
)

from database import (
    change_status,
    get_bookings
)


API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"



# ==================================
# ОТПРАВКА ЗАЯВКИ АДМИНАМ
# ==================================

def send_to_telegram(
        product,
        name,
        phone,
        image_url=None,
        channel_message_id=None,
        photo=None
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


    for admin_id in ADMIN_IDS:


        try:


            # =========================
            # 1. ЕСЛИ ЕСТЬ ID СООБЩЕНИЯ
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
                    "FORWARD RESULT:",
                    response.text,
                    flush=True
                )


                requests.post(

                    f"{API_URL}/sendMessage",

                    data={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )


            # =========================
            # 2. ЕСЛИ ЕСТЬ PHOTO FILE_ID
            # =========================

            elif photo:


                response = requests.post(

                    f"{API_URL}/sendPhoto",

                    data={

                        "chat_id": admin_id,

                        "photo": photo,

                        "caption": text

                    },

                    timeout=20

                )


                print(
                    "SEND PHOTO RESULT:",
                    response.text,
                    flush=True
                )



            # =========================
            # 3. ПРОСТО ТЕКСТ
            # =========================

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
                    "SEND TEXT RESULT:",
                    response.text,
                    flush=True
                )



        except Exception as e:


            print(
                "TELEGRAM ERROR:",
                e,
                flush=True
            )





# ==================================
# ПОСТ В КАНАЛ
# ==================================

def send_to_channel(
        text,
        photo=None,
        button=None
):


    try:


        if photo:


            payload = {

                "chat_id": TG_CHANNEL_CHAT_ID,

                "photo": photo,

                "caption": text

            }


            if button:

                payload["reply_markup"] = {

                    "inline_keyboard":[

                        [

                            {

                                "text": "🟢 Забронировать",

                                "url": button

                            }

                        ]

                    ]

                }


            response = requests.post(

                f"{API_URL}/sendPhoto",

                json=payload,

                timeout=20

            )



        else:


            response = requests.post(

                f"{API_URL}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": text

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
            f"✅ Статус заявки #{booking_id} изменён"
        )




    elif text == "/list":


        rows = get_bookings()


        msg = "📋 Последние заявки\n\n"


        for r in rows[:10]:


            msg += (

                f"#{r['id']} | "
                f"{r['product']} | "
                f"{r['status']}\n"

            )


        send_func(msg)





# ==================================
# ПОСТИНГ ИЗ ТГ
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
