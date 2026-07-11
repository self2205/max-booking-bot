import json

from fastapi import APIRouter, Request

from states import (
    get_state,
    set_state,
    clear_state
)

from database import (
    get_product,
    get_booking
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
    # ЗАПУСК ПО КНОПКЕ ИЗ КАНАЛА
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
            "PAYLOAD:",
            payload,
            flush=True
        )


        product_data = get_product(
            payload
        )


        if product_data:


            set_state(

                user_id,

                "WAIT_NAME",

                {

                    "product": product_data.get(
                        "product"
                    ),

                    "image_url": product_data.get(
                        "image_url"
                    ),

                    "channel_message_id": product_data.get(
                        "channel_message_id"
                    ),

                    "client_chat_id": chat_id

                }

            )


            send_message_max(

                chat_id,

                f"""
🟢 Бронирование

📦 {product_data.get("product")}

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
    # CALLBACK КНОПКИ
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


        user_id = (
            callback.get("user_id")
            or callback.get("user", {}).get("user_id")
        )


        chat_id = (
            data.get("message", {})
            .get("recipient", {})
            .get("chat_id")
        )


        print(
            "CALLBACK DATA:",
            callback,
            flush=True
        )


        print(
            "CALLBACK PAYLOAD:",
            payload,
            flush=True
        )


        print(
            "CALLBACK USER:",
            user_id,
            "CHAT:",
            chat_id,
            flush=True
        )

        # ==========================
        # НАПИСАТЬ МЕНЕДЖЕРУ
        # ==========================

        if payload and payload.startswith(
            "reply_client_"
        ):


            booking_id = payload.replace(
                "reply_client_",
                ""
            )


            print(
                "REPLY CLIENT BOOKING:",
                booking_id,
                flush=True
            )


            booking = get_booking(
                int(booking_id)
            )


            if not booking:


                send_message_max(

                    chat_id,

                    "❌ Заявка не найдена"

                )


                return {
                    "ok": True
                }



            set_state(

                user_id,

                "WAIT_CLIENT_MESSAGE",

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
                "Ваше сообщение будет отправлено."

            )


            return {
                "ok": True
            }


        return {
            "ok": True
        }



    # ==========================
    # ОБЫЧНЫЕ СООБЩЕНИЯ
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


    print(
        "TEXT:",
        text,
        flush=True
    )


    state = get_state(
        user_id
    )


    print(
        "STATE:",
        state,
        flush=True
    )

    # ==========================
    # СООБЩЕНИЕ МЕНЕДЖЕРУ
    # ==========================

    if state and state["state"] == "WAIT_CLIENT_MESSAGE":


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

✉️ Сообщение:
{text}
"""

            )


        clear_state(
            user_id
        )


        send_message_max(

            chat_id,

            "✅ Сообщение отправлено менеджеру."

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
""",

            buttons=[

                [

                    {
                        "type": "callback",
                        "text": "💬 Написать менеджеру",
                        "payload": f"reply_client_{booking_id}"
                    }

                ]

            ]

        )


        return {
            "ok": True
        }



    # ==========================
    # НЕТ СОСТОЯНИЯ
    # ==========================

    return {
        "ok": True
    }
