import requests
from config import MAX_TOKEN

def send_message_max(data, text: str):
    try:
        message = data.get("message", {})
        recipient = message.get("recipient", {})
        chat_id = recipient.get("chat_id")

        url = f"https://platform-api2.max.ru/messages?chat_id={chat_id}"

        headers = {
            "Authorization": MAX_TOKEN,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=10
        )

        print("MAX STATUS:", response.status_code)
        print("MAX RESPONSE:", response.text)

    except Exception as e:
        print("MAX ERROR:", e)
