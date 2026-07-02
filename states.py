# простое хранение состояния пользователей в памяти

user_states = {}

def set_state(user_id: int, state: str, data: dict = None):
    user_states[user_id] = {
        "state": state,
        "data": data or {}
    }


def get_state(user_id: int):
    return user_states.get(user_id)


def clear_state(user_id: int):
    user_states.pop(user_id, None)
