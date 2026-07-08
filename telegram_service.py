import requests

from config import (
    TG_TOKEN,
    ADMIN_IDS,
    TG_CHANNEL_CHAT_ID
)


from database import (
    change_status,
    get_bookings,
    save_telegram_message_id,
    get_booking
)



API_URL = f"https://api.telegram.org/bot{TG_TOKEN}"





# ==================================
# КНОПКИ ЗАЯВКИ
# ==================================

def booking_keyboard(booking_id):

    return {

        "inline_keyboard": [

            [

                {
                    "text": "💬 Ответить",
                    "callback_data": f"reply_{booking_id}"
                }

            ],

            [

                {
                    "text": "✅ Выполнено",
                    "callback_data": f"done_{booking_id}"
                },

                {
                    "text": "❌ Отменить",
                    "callback_data": f"cancel_{booking_id}"
                }

            ]

        ]

    }





# ==================================
# ОТПРАВКА ЗАЯВКИ АДМИНАМ
# ==================================

def send_to_telegram(
        booking_id,
        product,
        name,
        phone,
        image_url=None,
        channel_message_id=None,
        photo=None
):


    text = f"""
📦 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ


🆔 Заявка №{booking_id}


🛍 Товар:
{product}


👤 Имя:
{name}


📞 Телефон:
{phone}
"""



    message_id = None



    for admin_id in ADMIN_IDS:


        try:


            payload = {

                "chat_id": admin_id,

                "reply_markup": booking_keyboard(
                    booking_id
                )

            }



            # ==========================
            # ЕСЛИ ЕСТЬ ФОТО
            # ==========================

            if photo:


                payload.update({

                    "photo": photo,

                    "caption": text

                })


                response = requests.post(

                    f"{API_URL}/sendPhoto",

                    json=payload,

                    timeout=20

                )



            else:


                payload.update({

                    "text": text

                })


                response = requests.post(

                    f"{API_URL}/sendMessage",

                    json=payload,

                    timeout=15

                )




            result = response.json()



            print(
                "SEND BOOKING RESULT:",
                result,
                flush=True
            )



            if result.get("ok"):


                message_id = result["result"]["message_id"]


                save_telegram_message_id(
                    booking_id,
                    message_id
                )

        except Exception as e:


            print(
                "TELEGRAM ERROR:",
                e,
                flush=True
            )



    return message_id







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


# ==================================
# CALLBACK BUTTONS
# ==================================

def handle_callback(callback):


    data = callback.get(
        "data",
        ""
    )


    if data.startswith("done_"):


        booking_id = int(
            data.replace(
                "done_",
                ""
            )
        )


        change_status(
            booking_id
        )


        return "✅ Заявка выполнена"



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


        return "❌ Заявка отменена"



    elif data.startswith("reply_"):


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

            return "❌ Заявка не найдена"



        return {

            "action": "reply",

            "chat_id": booking["client_chat_id"]

        }


    return None
