from database import save_booking
from telegram_service import send_to_telegram



def create_booking(
        product,
        name,
        phone,
        image_url=None,
        channel_message_id=None
):


    booking_id = save_booking(

        product=product,

        name=name,

        phone=phone,

        image_url=image_url

    )



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
