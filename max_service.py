import requests
import urllib3
from config import MAX_TOKEN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# ОТПРАВИТЬ СООБЩЕНИЕ В MAX
# =========================
def send_message_max(chat_id, text):
    url = "https://platform-api2.max.ru/messages"

    headers = {
        "Authorization": MAX_TOKEN,
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

        try:
            return r.json()
        except:
            return {}

    except Exception as e:
        print("MAX ERROR:", e)
        return {}


# =========================
# ПОЛУЧИТЬ ПОЛНОЕ СООБЩЕНИЕ
# =========================
def get_max_message(mid):
    url = f"https://platform-api2.max.ru/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=10,
            verify=False
        )

        print("MAX FULL MESSAGE:", r.text)

        return r.json()

    except Exception as e:
        print("GET MESSAGE ERROR:", e)
        return {}


# =========================
# КАРТИНКА ИЗ WEBHOOK
# =========================
def extract_image_from_webhook(message):
    body = message.get("body", {})

    for a in body.get("attachments", []):
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None


# =========================
# КАРТИНКА ИЗ API
# =========================
def extract_image(data):
    body = data.get("message", {}).get("body", {})

    for a in body.get("attachments", []):
        if a.get("type") == "image":
            return a.get("url")

    for m in body.get("media", []):
        if m.get("type") == "image":
            return m.get("url")

    return None
