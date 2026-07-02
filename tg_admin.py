from database import change_status, get_bookings

ADMIN_TG_ID = 441725473  # твой Telegram ID


def handle_tg_admin(message, send_tg):
    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    if user_id != ADMIN_TG_ID:
        return

    if text.startswith("/status"):
        try:
            booking_id = int(text.split()[1])
        except:
            send_tg("❌ Используй: /status 12")
            return

        change_status(booking_id)
        send_tg(f"✅ Статус заявки #{booking_id} обновлён")
        return

    if text == "/list":
        rows = get_bookings()
        msg = "📋 Заявки:\n\n"

        for r in rows[:10]:
            msg += f"{r['id']} | {r['product']} | {r['status']}\n"

        send_tg(msg)
