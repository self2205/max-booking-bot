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
    # КНОПКИ / СТАРТ БОТА
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
            payload
        )



        # ==========================
        # КНОПКА ОТВЕТИТЬ МЕНЕДЖЕРУ
        # ==========================

        if payload.startswith("reply_client_"):


            booking_id = payload.replace(
                "reply_client_",
                ""
            )


            state = get_state(
                user_id
            )


            if state:


                set_state(

                    user_id,

                    "WAIT_MANAGER_MESSAGE",

                    {

                        "booking_id": booking_id,

                        "product": state["data"].get(
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
        # КНОПКА БРОНИРОВАНИЯ ТОВАРА
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

                "👋 Привет!\n\n"
                "Что хотите забронировать?"

            )



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
    # ИМЯ
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
    # ТЕЛЕФОН
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



        set_state(

            user_id,

            "WAIT_MANAGER_MESSAGE",

            {

                "booking_id": booking_id,

                "product": product

            }

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

Если нужно уточнить детали — нажмите кнопку ниже.
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
    # НЕТ БРОНИ
    # ==========================

    send_message_max(

        chat_id,

        "ℹ️ Для связи с менеджером сначала оформите бронирование товара."

    )


    return {
        "ok": True
    }
