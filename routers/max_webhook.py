import json

from fastapi import APIRouter, Request

from states import (
    get_state,
    set_state,
    clear_state
)

from database import get_product

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

    data = await request.json()


    print("\n========== MAX WEBHOOK ==========")

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )

    print("=================================\n")



    update_type = data.get(
        "update_type"
    )



    # ==========================
    # ЗАПУСК ПО КНОПКЕ БРОНИ
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


            set_state(

                user_id,

                "WAIT_PRODUCT",

                {}

            )


            send_message_max(

                chat_id,

                "👋 Привет!\n\nЧто хотите забронировать?"

            )



        return {
            "ok": True
        }





    # ==========================
    # ОБРАБОТКА СООБЩЕНИЙ
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
    # ОТВЕТ МЕНЕДЖЕРУ
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
"""

            )



        send_message_max(

            chat_id,

            "✅ Сообщение отправлено менеджеру.\n\n"
            "Мы скоро ответим вам."

        )


        clear_state(
            user_id
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




        clear_state(
            user_id
        )



        # сохраняем возможность ответа менеджеру

        set_state(

            user_id,

            "WAIT_MANAGER_MESSAGE",

            {

                "booking_id": booking_id,

                "product": state["data"]["product"]

            }

        )



        send_message_max(

            chat_id,


            f"""
✅ Заявка на бронирование создана!

📦 Товар:
{state["data"]["product"]}

🆔 Номер:
#{booking_id}


Мы свяжемся с вами в ближайшее время.

Если нужно уточнить детали — нажмите кнопку ниже.
""",

        )


        return {
            "ok": True
        }





    # ==========================
    # НЕТ АКТИВНОЙ ЗАЯВКИ
    # ==========================

    send_message_max(

        chat_id,

        "ℹ️ Для связи с менеджером сначала оформите бронирование товара."

    )


    return {
        "ok": True
    }
