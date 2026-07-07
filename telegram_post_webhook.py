import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post


API_URL = (
    f"https://api.telegram.org/bot{TG_POST_TOKEN}"
)



def get_updates():

    response = requests.get(
        f"{API_URL}/getUpdates",
        timeout=30
    )

    return response.json()



def process_updates():

    data = get_updates()


    for update in data.get("result", []):


        message = update.get("message")


        if not message:
            continue


        photo = message.get("photo")

        caption = message.get(
            "caption",
            ""
        )


        if not photo:
            continue


        file_id = photo[-1]["file_id"]


        product = caption


        if not product:

            product = "Товар"



        send_post(

            product=product,

            image_url=file_id

        )



if __name__ == "__main__":

    process_updates()
