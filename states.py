# простое хранение состояния пользователей в памяти

user_states = {}


# ==========================
# STATES
# ==========================

WAIT_PRODUCT = "wait_product"
WAIT_NAME = "wait_name"
WAIT_PHONE = "wait_phone"

# новое состояние:
# клиент пишет менеджеру после бронирования
WAIT_MANAGER_MESSAGE = "wait_manager_message"



# ==========================
# SET STATE
# ==========================

def set_state(user_id: int, state: str, data: dict = None):

    user_states[user_id] = {

        "state": state,

        "data": data or {}

    }



# ==========================
# GET STATE
# ==========================

def get_state(user_id: int):

    return user_states.get(
        user_id
    )



# ==========================
# CLEAR STATE
# ==========================

def clear_state(user_id: int):

    user_states.pop(
        user_id,
        None
    )
