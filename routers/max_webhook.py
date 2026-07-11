if payload.startswith("reply_client_"):


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

            "❌ Бронь не найдена"

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
    # ОБРАБАТЫВАЕМ ТОЛЬКО СООБЩЕНИЯ
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




        # НЕ ставим WAIT_MANAGER_MESSAGE здесь
        # клиент сначала должен нажать кнопку


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



        return {



            "ok": True


        }

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
