# ==================================
# ХРАНЕНИЕ РЕЖИМА ОТВЕТА КЛИЕНТУ
# ==================================


active_replies = {}



# ==========================
# ВКЛЮЧИТЬ ОТВЕТ
# ==========================

def set_reply_mode(
        admin_id,
        client_chat_id
):

    active_replies[admin_id] = client_chat_id



# ==========================
# ПРОВЕРИТЬ РЕЖИМ
# ==========================

def get_reply_client(
        admin_id
):

    return active_replies.get(
        admin_id
    )



# ==========================
# ОТКЛЮЧИТЬ
# ==========================

def clear_reply_mode(
        admin_id
):

    if admin_id in active_replies:

        del active_replies[admin_id]
