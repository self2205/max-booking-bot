from database import save_booking
from telegram_service import send_to_telegram


def create_booking(product: str, name: str, phone: str):
    """
    Создает заявку:
    - сохраняет в PostgreSQL
    - отправляет в Telegram
    """

    booking_id = save_booking(
        product=product,
        name=name,
        phone=phone
    )

    send_to_telegram(
        product=product,
        name=name,
        phone=phone
    )

    print("\n========== НОВАЯ ЗАЯВКА ==========")
    print(f"ID: {booking_id}")
    print(f"Товар: {product}")
    print(f"Имя: {name}")
    print(f"Телефон: {phone}")
    print("=================================\n")

    return booking_id
