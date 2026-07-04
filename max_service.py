import requests
from config import MAX_TOKEN


# =========================
# 1. ПОЛУЧИТЬ ПОЛНОЕ СООБЩЕНИЕ
# =========================
def get_max_message(mid: str):
    url = f"https://platform-api2.max.ru/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    r = requests.get(url, headers=headers, timeout=10, verify=False)

    print("MAX FULL MESSAGE:", r.text)

    try:
        return r.json()
    except Exception:
        return {}


# =========================
# 2. ОТПРАВИТЬ СООБЩЕНИЕ В MAX
# =========================
def send_message_max(chat_id: str, text: str):
    url = "https://platform-api2.max.ru/messages"

    headers = {
        "Authorization": MAX_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    r = requests.post(url, json=payload, headers=headers, timeout=10, verify=False)

    print("SEND RESPONSE:", r.text)

    try:
        return r.json()
    except Exception:
        return {}


# =========================
# 3. ДОСТАТЬ КАРТИНКУ ИЗ MESSAGE (API)
# =========================
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


# =========================
# 4. ДОСТАТЬ КАРТИНКУ ИЗ WEBHOOK
# =========================
def extract_image_from_webhook(message):
    body = message.get("body", {})

    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
