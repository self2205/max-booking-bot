from database import save_booking
from telegram_service import send_to_telegram



def create_booking(
        product,
        name,
        phone,
        image_url=None,
        channel_message_id=None,
        client_chat_id=None
):

    """
    Создает заявку:

    - сохраняет в PostgreSQL
    - сохраняет MAX chat_id клиента
    - отправляет заявку админам в Telegram
    """



    booking_id = save_booking(

        product=product,

        name=name,

        phone=phone,

        image_url=image_url,

        client_chat_id=client_chat_id

    )



    telegram_message_id = send_to_telegram(

        booking_id=booking_id,

        product=product,

        name=name,

        phone=phone,

        image_url=image_url,

        photo=image_url,

        channel_message_id=channel_message_id

    )



    print("\n========== НОВАЯ ЗАЯВКА ==========")



    print(
        f"ID: {booking_id}"
    )


    print(
        f"Товар: {product}"
    )


    print(
        f"Имя: {name}"
    )


    print(
        f"Телефон: {phone}"
    )


    print(
        f"Фото: {image_url}"
    )


    print(
        f"MAX CHAT ID: {client_chat_id}"
    )


    print(
        f"TELEGRAM MESSAGE ID: {telegram_message_id}"
    )


    print(
        "=================================\n"
    )



    return booking_id
