import requests
import urllib3
from config import MAX_TOKEN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://platform-api2.max.ru"


# =========================
# ОТПРАВКА СООБЩЕНИЯ
# =========================
def send_message_max(chat_id, text):
    url = f"{API_URL}/messages"

    headers = {
        "Authorization": MAX_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "chat_id": chat_id
        },
        "body": {
            "text": text
        }
    }

    try:
        r = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15,
            verify=False
        )

        print("========== SEND TO MAX ==========")
        print("STATUS:", r.status_code)
        print("BODY:", r.text)
        print("=================================")

        try:
            return r.json()
        except Exception:
            return {}

    except Exception as e:
        print("MAX ERROR:", e)
        return {}


# =========================
# ПОЛУЧИТЬ СООБЩЕНИЕ
# =========================
def get_max_message(mid):
    url = f"{API_URL}/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    r = requests.get(
        url,
        headers=headers,
        timeout=15,
        verify=False
    )

    print(r.text)

    try:
        return r.json()
    except Exception:
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
            return a.get("payload", {}).get("url")

    for m in body.get("media", []):
        if m.get("type") == "image":
            return m.get("url")

    return None
