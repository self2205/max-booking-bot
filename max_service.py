import requests
from config import MAX_TOKEN
import urllib3

# убрать ssl warnings (чтобы лог не засорялся)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# 1. ПОЛУЧИТЬ СООБЩЕНИЕ
# =========================
def get_max_message(mid: str):
    url = f"https://platform-api2.max.ru/messages/{mid}"

    headers = {
        "Authorization": f"Bearer {MAX_TOKEN}"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        print("MAX FULL MESSAGE:", r.text)
        return r.json()

    except Exception as e:
        print("GET MAX ERROR:", e)
        return {}


# =========================
# 2. ОТПРАВИТЬ СООБЩЕНИЕ
# =========================
def send_message_max(chat_id: int | str, text: str):
    url = "https://platform-api2.max.ru/messages"

    headers = {
        "Authorization": f"Bearer {MAX_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        r = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
            verify=False
        )

        print("STATUS:", r.status_code)
        print("SEND RESPONSE:", r.text)

        return r.json() if r.text else {}

    except Exception as e:
        print("MAX ERROR:", e)
        return {"error": str(e)}


# =========================
# 3. КАРТИНКА (API MESSAGE)
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
# 4. КАРТИНКА (WEBHOOK)
# =========================
def extract_image_from_webhook(message):
    body = message.get("body", {})
    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
