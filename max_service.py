import requests
import urllib3
from config import MAX_TOKEN

# отключаем SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://platform-api2.max.ru"


# =========================
# 1. GET MESSAGE
# =========================
def get_max_message(mid: str):
    url = f"{BASE_URL}/messages/{mid}"

    headers = {
        "Authorization": MAX_TOKEN
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        print("MAX FULL MESSAGE:", r.text)
        return r.json()
    except Exception as e:
        print("GET MAX ERROR:", e)
        return {}


# =========================
# 2. SEND MESSAGE
# =========================
def send_message_max(chat_id: str | int, text: str):
    url = f"{BASE_URL}/messages"

    headers = {
        "Authorization": MAX_TOKEN,   # MAX НЕ BEARER
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
            verify=False   # <<< ВОТ ЭТО ОБЯЗАТЕЛЬНО
        )

        print("STATUS:", r.status_code)
        print("SEND RESPONSE:", r.text)

        try:
            return r.json()
        except:
            return {"raw": r.text}

    except Exception as e:
        print("MAX ERROR:", e)
        return {"error": str(e)}


# =========================
# 3. IMAGE FROM WEBHOOK
# =========================
def extract_image_from_webhook(message):
    body = message.get("body", {})
    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
