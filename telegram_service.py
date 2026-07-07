import requests
import re

from config import (
    TG_TOKEN,
    TG_CHANNEL_CHAT_ID,
    ADMIN_IDS
)

from database import change_status, get_bookings


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
def send_to_telegram(product, name, phone, image_url=None):

    text = f"""📦 НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ

🛍 Товар:
{product}

👤 Имя:
{name}

📞 Телефон:
{phone}
"""


    try:

        for admin_id in ADMIN_IDS:


            if image_url:

                requests.post(

                    f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",

                    data={

                        "chat_id": admin_id,

                        "photo": image_url,

                        "caption": text

                    },

                    timeout=15

                )


            else:

                requests.post(

                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                    data={

                        "chat_id": admin_id,

                        "text": text

                    },

                    timeout=15

                )


    except Exception as e:

        print(
            "Telegram error:",
            e
        )




# ==========================
# ОТПРАВКА ПОСТА В КАНАЛ
# ==========================
def send_to_channel(product: str):

    product = clean_product(product)


    product_url = (
        "https://max.ru/se13456903_bot?start=product_"
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


        resp = requests.post(

            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

            json=payload,

            timeout=15

        )


        print(
            "CHANNEL:",
            resp.status_code
        )


        print(
            resp.text
        )


    except Exception as e:

        print(
            "Channel error:",
            e
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



    send_to_channel(text)


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
