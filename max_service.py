import requests


from config import MAX_TOKEN


def send_message_max(data, text):
    """
    Отправка сообщения пользователю в MAX
    """

    try:
        message = data.get("message", {})
        recipient = message.get("recipient", {})

        chat_id = recipient.get("chat_id")

        if not chat_id:
            print("MAX ERROR: chat_id not found")
            return

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

        print("========== SEND TO MAX ==========")
        print("URL:", url)
        print("Payload:", payload)
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("=================================")

    except Exception as e:
        print("MAX ERROR:", e)
