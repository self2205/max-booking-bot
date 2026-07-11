import json

from fastapi import APIRouter, Request

from states import (
    get_state,
    set_state,
    clear_state
)

from database import (
    get_product,
    get_booking,
    change_status
)

from booking_service import create_booking

from max_service import send_message_max

from config import ADMIN_IDS

from telegram_admin_listener import send_telegram


router = APIRouter()



# ==========================
# MAX WEBHOOK
# ==========================

@router.post("/webhook")
async def max_webhook(request: Request):

    print("🔥 WEBHOOK HIT", flush=True)


    data = await request.json()


    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        flush=True
    )


    update_type = data.get(
        "update_type"
    )


    print(
        "UPDATE TYPE:",
        update_type,
        flush=True
    )



    # ==========================
    # КНОПКИ / START
    # ==========================

    if update_type == "bot_started":


        user_id = data.get(
            "user_id"
        )


        chat_id = data.get(
            "chat_id"
        )


        payload = (

            data.get("payload")

            or data.get("start")

            or data.get("parameter")

            or ""

        )


        print(
            "BUTTON PAYLOAD:",
            payload,
            flush=True
        )



        # ==========================
        # НАЧАЛО БРОНИРОВАНИЯ
        # ==========================


        product_data = get_product(
            payload
        )


        if product_data:


            product = product_data.get(
                "product"
            )


            image_url = product_data.get(
                "image_url"
            )


            channel_message_id = product_data.get(
                "channel_message_id"
            )


            set_state(

                user_id,

                "WAIT_NAME",

                {

                    "product": product,

                    "image_url": image_url,

                    "channel_message_id": channel_message_id,

                    "client_chat_id": chat_id

                }

            )


            send_message_max(

                chat_id,


                f"""
🟢 Бронирование

📦 {product}

✍️ Введите ваше имя
"""

            )


        else:


            send_message_max(

                chat_id,

                "👋 Привет!\n\nЧто хотите забронировать?"

            )


        return {

            "ok": True

        }



    # ==========================
    # CALLBACK КНОПКИ MAX
    # ==========================

    if update_type == "message_callback":


        print(
            "🔥 CALLBACK RECEIVED",
            flush=True
        )


        callback = data.get(
            "callback",
            {}
        )


        payload = callback.get(
            "payload"
        )


        user_id = callback.get(
            "user_id"
        )


        chat_id = callback.get(
            "chat_id"
        )


        print(
            "PAYLOAD:",
            payload,
            flush=True
        )


        print(
            "USER:",
            user_id,
            "CHAT:",
            chat_id,
            flush=True
        )

        # ==========================
        # КНОПКА "НАПИСАТЬ МЕНЕДЖЕРУ"
        # ==========================

        if payload and payload.startswith(
            "reply_client_"
        ):


            booking_id = payload.replace(
                "reply_client_",
                ""
            )


            print(
                "REPLY BOOKING:",
                booking_id,
                flush=True
            )


            booking = get_booking(
                int(booking_id)
            )


            if not booking:


                send_message_max(

                    chat_id,

                    "❌ Бронь не найдена."

                )


                return {

                    "ok": True

                }



            set_state(

                user_id,

                "WAIT_MANAGER_MESSAGE",

                {

                    "booking_id": booking_id,

                    "product": booking.get(

                        "product",

                        "Не указан"

                    )

                }

            )


            send_message_max(

                chat_id,

                "💬 Напишите сообщение менеджеру.\n\n"
                "Мы ответим вам в ближайшее время."

            )


            return {

                "ok": True

            }



        # ==========================
        # КНОПКА "ОТМЕНИТЬ БРОНЬ"
        # ==========================

        if payload and payload.startswith(
            "cancel_booking_"
        ):


            booking_id = payload.replace(
                "cancel_booking_",
                ""
            )


            booking = get_booking(
                int(booking_id)
            )


            if booking:


                change_status(
                    int(booking_id)
                )


                for admin in ADMIN_IDS:


                    send_telegram(

                        admin,


                        f"""
❌ Клиент отменил бронирование

📦 Товар:
{booking.get("product","Не указан")}

🆔 Бронь:
#{booking_id}
"""

                    )



            clear_state(
                user_id
            )



            send_message_max(

                chat_id,

                "✅ Ваше бронирование отменено."

            )


            return {

                "ok": True

            }



        return {

            "ok": True

        }



    # ==========================
    # ТОЛЬКО СООБЩЕНИЯ
    # ==========================


    if update_type != "message_created":


        return {

            "ok": True

        }



    message = data.get(
        "message",
        {}
    )



    chat_id = message.get(
        "recipient",
        {}
    ).get(
        "chat_id"
    )


    user_id = message.get(
        "sender",
        {}
    ).get(
        "user_id"
    )


    text = message.get(
        "body",
        {}
    ).get(
        "text",
        ""
    )



    state = get_state(
        user_id
    )



    # ==========================
    # СООБЩЕНИЕ МЕНЕДЖЕРУ
    # ==========================


    if state and state["state"] == "WAIT_MANAGER_MESSAGE":


        booking_id = state["data"].get(
            "booking_id"
        )


        product = state["data"].get(
            "product",
            "Не указан"
        )



        for admin in ADMIN_IDS:


            send_telegram(

                admin,


                f"""
💬 Сообщение от клиента

📦 Товар:
{product}

🆔 Бронь:
#{booking_id}

💬 Сообщение:
{text}
""",

                buttons=[

                    [

                        {

                            "text": "💬 Ответить клиенту",

                            "callback_data": f"reply_{booking_id}"

                        }

                    ]

                ]

            )



        send_message_max(

            chat_id,

            "✅ Сообщение отправлено менеджеру.\n\n"
            "Мы скоро ответим."

        )


        return {

            "ok": True

        }

    # ==========================
    # ВВОД ИМЕНИ
    # ==========================


    if state and state["state"] == "WAIT_NAME":


        state["data"]["name"] = text



        set_state(

            user_id,

            "WAIT_PHONE",

            state["data"]

        )



        send_message_max(

            chat_id,

            "📞 Введите ваш телефон"

        )



        return {

            "ok": True

        }




    # ==========================
    # ВВОД ТЕЛЕФОНА
    # ==========================


    if state and state["state"] == "WAIT_PHONE":


        state["data"]["phone"] = text



        booking_id = create_booking(

            product=state["data"]["product"],

            name=state["data"]["name"],

            phone=state["data"]["phone"],

            image_url=state["data"].get(
                "image_url"
            ),

            channel_message_id=state["data"].get(
                "channel_message_id"
            ),

            client_chat_id=state["data"].get(
                "client_chat_id"
            )

        )



        product = state["data"]["product"]



        clear_state(

            user_id

        )



        send_message_max(

            chat_id,


            f"""
✅ Заявка создана!

📦 Товар:
{product}

🆔 Номер:
#{booking_id}

Мы свяжемся с вами в ближайшее время.

Если нужно уточнить детали — воспользуйтесь кнопками ниже.
""",


            buttons=[

                [

                    {
                        "type": "callback",
                        "text": "💬 Написать менеджеру",
                        "payload": f"reply_client_{booking_id}"
                    }

                ],

                [

                    {
                        "type": "callback",
                        "text": "❌ Отменить бронирование",
                        "payload": f"cancel_booking_{booking_id}"
                    }

                ]

            ]

        )


    # ==========================
    # НЕТ АКТИВНОЙ БРОНИ
    # ==========================


    send_message_max(

        chat_id,

        "ℹ️ Для связи с менеджером сначала оформите бронирование товара."

    )


    return {

        "ok": True

    }
