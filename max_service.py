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

    params = {
        "chat_id": chat_id
    }

    payload = {
        "text": text
    }

    r = requests.post(
        url,
        headers=headers,
        params=params,
        json=payload,
        timeout=15,
        verify=False
    )

    print("URL:", r.request.url)
    print("STATUS:", r.status_code)
    print("BODY:", r.text)

    return r.json() if "application/json" in r.headers.get("Content-Type", "") else {}


# =========================
# ПОЛУЧИТЬ СООБЩЕНИЕ
# =========================
def send_message_max(chat_id, text):
    url = f"{API_URL}/messages?chat_id={chat_id}"

    headers = {
        "Authorization": MAX_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text
    }

    r = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15,
        verify=False
    )

    print("URL:", url)
    print("STATUS:", r.status_code)
    print("BODY:", r.text)

    return r.json() if r.headers.get("content-type", "").startswith("application/json") else {}


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
