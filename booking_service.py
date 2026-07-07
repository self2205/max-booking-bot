from database import (
    save_booking,
    get_product
)

from telegram_service import send_to_telegram



def create_booking(
        product,
        name,
        phone,
        image_url=None
):
    """
    Создает заявку:
    - сохраняет в PostgreSQL
    - отправляет в Telegram админам с фото из канала
    """



    # ==========================
    # ИЩЕМ ПОСТ В КАНАЛЕ
    # ==========================

    channel_message_id = None


    try:

        rows = get_product_by_name(product)


        if rows:

            channel_message_id = rows.get(
                "channel_message_id"
            )


    except Exception as e:

        print(
            "GET CHANNEL MESSAGE ERROR:",
            e
        )





    # ==========================
    # СОХРАНЯЕМ ЗАЯВКУ
    # ==========================

    booking_id = save_booking(

        product=product,

        name=name,

        phone=phone,

        image_url=image_url

    )





    # ==========================
    # ОТПРАВЛЯЕМ АДМИНАМ
    # ==========================

    send_to_telegram(

        product=product,

        name=name,

        phone=phone,

        image_url=image_url,

        channel_message_id=channel_message_id

    )





    print(
        "\n========== НОВАЯ ЗАЯВКА =========="
    )

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
        f"CHANNEL MESSAGE ID: {channel_message_id}"
    )

    print(
        "=================================\n"
    )


    return booking_id
