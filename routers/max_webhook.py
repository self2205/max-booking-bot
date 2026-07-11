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
    # START / КНОПКА ИЗ КАНАЛА
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
    # START / КНОПКА ИЗ КАНАЛА
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
