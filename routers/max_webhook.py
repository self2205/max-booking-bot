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
            "PAYLOAD:",
            payload,
            flush=True
        )


        # запуск бронирования товара

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
    # CALLBACK КНОПКА
    # ==========================

    if update_type == "message_callback":


        print(
            "🔥 CALLBACK",
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
            "CALLBACK PAYLOAD:",
            payload,
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
                "Ваше сообщение будет отправлено менеджеру."

            )


            return {
                "ok": True
            }


        return {
            "ok": True
        }

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
            "PAYLOAD:",
            payload,
            flush=True
        )


        # запуск бронирования товара

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
    # CALLBACK КНОПКА
    # ==========================

    if update_type == "message_callback":


        print(
            "🔥 CALLBACK",
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
            "CALLBACK PAYLOAD:",
            payload,
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
                "Ваше сообщение будет отправлено менеджеру."

            )


            return {
                "ok": True
            }


        return {
            "ok": True
        }

    # ==========================
    # НЕТ АКТИВНОГО СОСТОЯНИЯ
    # ==========================

    send_message_max(

        chat_id,

        "ℹ️ Для связи с менеджером сначала оформите бронирование товара."

    )


    return {

        "ok": True

    }
