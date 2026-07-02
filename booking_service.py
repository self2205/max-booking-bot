from database import save_booking
from telegram_service import send_to_telegram


def create_booking(product: str, name: str, phone: str):
    """
    Сохраняет заявку в БД и отправляет её в Telegram.
    """

    save_booking(
        product,
        name,
        phone
    )

    send_to_telegram(
        product,
        name,
        phone
    )

    print("\n========== НОВОЕ БРОНИРОВАНИЕ ==========")
    print(f"Товар: {product}")
    print(f"Имя: {name}")
    print(f"Телефон: {phone}")
    print("=================================\n")
