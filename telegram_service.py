import requests

from config import (
    TG_TOKEN,
    TG_CHANNEL_CHAT_ID,
    ADMIN_IDS,
    MAX_BOT_USERNAME
)

from database import (
    change_status,
    get_bookings
)



# ==========================
# ОЧИСТКА ТОВАРА
# ==========================

def clean_product(text: str):

    if not text:
        return "Товар"

    return text.strip()



# ==========================
# ОТПРАВКА ЗАЯВКИ АДМИНАМ
# ==========================

def send_to_telegram(
        product,
        name,
        phone,
        image_url=None,
        channel_message_id=None
):


    text = f"""📦 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ

🛍 Товар:
{product}

👤 Имя:
{name}

📞 Телефон:
{phone}
"""



    for admin_id in ADMIN_IDS:


        try:


            # ==========================
            # ЕСЛИ ЕСТЬ ПОСТ В КАНАЛЕ
            # КОПИРУЕМ ЕГО С ФОТО
            # ==========================

            if channel_message_id:


                response = requests.post(

                    f"https://api.telegram.org/bot{TG_TOKEN}/copyMessage",

                    json={

                        "chat_id": admin_id,

                        "from_chat_id": TG_CHANNEL_CHAT_ID,

                        "message_id": channel_message_id

                    },

                    timeout=15

                )


                # после фото отправляем данные заявки

                requests.post(

                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                    json={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )



            else:


                response = requests.post(

                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                    json={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )





            print(
                "TELEGRAM ADMIN:",
                admin_id,
                flush=True
            )


            print(
                response.text,
                flush=True
            )




        except Exception as e:


            print(
                "TELEGRAM SEND ERROR:",
                e,
                flush=True
            )






# ==========================
# ОТПРАВКА ПОСТА В КАНАЛ
# ==========================

def send_to_channel(product: str):

    product = clean_product(product)



    product_url = (

        f"https://max.ru/{MAX_BOT_USERNAME}?start=product_"

        + requests.utils.quote(product)

    )



    payload = {


        "chat_id": TG_CHANNEL_CHAT_ID,


        "text": f"📦 {product}",


        "reply_markup": {


            "inline_keyboard": [

                [

                    {

                        "text": "🟢 Забронировать",

                        "url": product_url

                    }

                ]

            ]

        }

    }



    try:


        response = requests.post(

            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

            json=payload,

            timeout=15

        )


        print(
            "CHANNEL RESPONSE:",
            response.text,
            flush=True
        )



    except Exception as e:


        print(
            "CHANNEL ERROR:",
            e,
            flush=True
        )






# ==========================
# ADMIN COMMANDS
# ==========================

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


        return





    if text == "/list":


        rows = get_bookings()


        msg = "📋 Последние заявки\n\n"


        for r in rows[:10]:


            msg += (

                f"#{r['id']} | "

                f"{r['product']} | "

                f"{r['status']}\n"

            )


        send_func(msg)

        return






# ==========================
# ГЕНЕРАТОР ПОСТОВ
# ==========================

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



    if not text:

        return False



    if text.startswith("/"):

        return False



    send_to_channel(
        text
    )


    send_func(
        "✅ Пост опубликован в канал."
    )


    return True






# ==========================
# MAIN DISPATCHER
# ==========================

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
