import requests
from config import MAX_TOKEN


# 1. Получаем полное сообщение по mid
def get_max_message(mid: str):
    url = f"https://platform-api2.max.ru/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    r = requests.get(url, headers=headers, timeout=10, verify=False)

    print("MAX FULL MESSAGE:", r.text)

    return r.json()


# 2. Достаём картинку из ответа MAX
def extract_image(data):
    body = data.get("message", {}).get("body", {})

    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("url")

    media = body.get("media", [])

    for m in media:
        if m.get("type") == "image":
            return m.get("url")

    return None

def extract_image_from_webhook(message):
    body = message.get("body", {})

    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
