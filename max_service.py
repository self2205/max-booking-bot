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

    try:
        r = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=15,
            verify=False
        )

        print("========== SEND TO MAX ==========")
        print("REQUEST URL:", r.request.url)
        print("REQUEST BODY:", payload)
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

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=15,
            verify=False
        )

        print("GET MESSAGE:", r.status_code)
        print(r.text)

        try:
            return r.json()
        except Exception:
            return {}

    except Exception as e:
        print("MAX ERROR:", e)
        return {}


# =========================
# КАРТИНКА ИЗ WEBHOOK
# =========================
def extract_image_from_webhook(message):

    body = message.get("body", {})

    attachments = body.get("attachments", [])

    for a in attachments:

        if a.get("type") != "image":
            continue

        payload = a.get("payload", {})

        if payload.get("url"):
            return payload.get("url")

        if payload.get("image", {}).get("url"):
            return payload["image"]["url"]

        if payload.get("image_url"):
            return payload.get("image_url")

    return None


# =========================
# КАРТИНКА ИЗ API
# =========================
def extract_image(data):

    body = data.get("message", {}).get("body", {})

    attachments = body.get("attachments", [])

    for a in attachments:

        if a.get("type") != "image":
            continue

        payload = a.get("payload", {})

        if payload.get("url"):
            return payload.get("url")

        if payload.get("image", {}).get("url"):
            return payload["image"]["url"]

        if payload.get("image_url"):
            return payload.get("image_url")


    media = body.get("media", [])

    for m in media:

        if m.get("type") == "image":

            if m.get("url"):
                return m.get("url")

            if m.get("image_url"):
                return m.get("image_url")


    return None
