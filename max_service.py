import requests
import config

MAX_TOKEN = config.MAX_TOKEN.strip()


def send_message_max(chat_id, text):
    url = "https://platform-api2.max.ru/messages"

    headers = {
        "Authorization": MAX_TOKEN,   # если у тебя раньше работало без Bearer
        "Content-Type": "application/json"
    }

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    r = requests.post(url, json=payload, headers=headers, timeout=10)

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    return r.json() if r.text else {}


def get_max_message(mid: str):
    url = f"https://platform-api2.max.ru/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    r = requests.get(url, headers=headers, timeout=10)
    return r.json()


def extract_image(data):
    body = data.get("message", {}).get("body", {})
    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("url")

    return None


def extract_image_from_webhook(message):
    body = message.get("body", {})
    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
