# ==========================
# Хранилище состояний пользователей
# ==========================

# user_id -> состояние
user_states = {}

# user_id -> данные заявки
user_data = {}


# Состояния
STATE_IDLE = "idle"
STATE_WAIT_PRODUCT = "wait_product"
STATE_WAIT_NAME = "wait_name"
STATE_WAIT_PHONE = "wait_phone"


def set_state(user_id: int, state: str):
    user_states[user_id] = state


def get_state(user_id: int):
    return user_states.get(user_id, STATE_IDLE)


def clear_state(user_id: int):
    user_states.pop(user_id, None)
    user_data.pop(user_id, None)


def set_data(user_id: int, key: str, value):
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id][key] = value


def get_data(user_id: int):
    return user_data.get(user_id, {})
