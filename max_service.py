import requests
import urllib3
from config import MAX_TOKEN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# SEND MESSAGE (FIXED)
# =========================
def send_message_max(recipient: dict, text: str):
    """
    recipient = message["message"]["recipient"]
    """

    url = "https://platform-api2.max.ru/messages"

    headers = {
        "Authorization": f"Bearer {MAX_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": recipient,
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
        print("RESPONSE:", r.text)

        return r.json() if r.text else {}

    except Exception as e:
        print("MAX ERROR:", e)
        return {"error": str(e)}


# =========================
# EXTRACT IMAGE (WEBHOOK)
# =========================
def extract_image_from_webhook(message):
    body = message.get("body", {})
    attachments = body.get("attachments", [])

    for a in attachments:
        if a.get("type") == "image":
            return a.get("payload", {}).get("url")

    return None
