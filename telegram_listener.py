import time
import requests

from config import TG_POST_TOKEN, ADMIN_IDS
from telegram_poster import send_post


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None



# ==========================
# ПОЛУЧЕНИЕ ОБНОВЛЕНИЙ
# ==========================

def get_updates():

    global offset

    params = {
        "timeout": 30
    }


    if offset:

        params["offset"] = offset


    try:

        response = requests.get(

            f"{API_URL}/getUpdates",

            params=params,

            timeout=35

        )

        return response.json()


    except Exception as e:

        print(
            "GET UPDATES ERROR:",
            e,
            flush=True
        )

        return {}




# ==========================
# ПОЛУЧЕНИЕ ССЫЛКИ НА ФОТО
# ==========================

def get_file_url(file_id):

    try:

        response = requests.get(

            f"{API_URL}/getFile",

            params={
                "file_id": file_id
            },

            timeout=15

        )


        data = response.json()


        if not data.get("ok"):

            print(
                "GET FILE ERROR:",
                data,
                flush=True
            )

            return None



        file_path = data["result"]["file_path"]



        return (

            f"https://api.telegram.org/file/bot"

            f"{TG_POST_TOKEN}/"

            f"{file_path}"

        )


    except Exception as e:


        print(
            "FILE URL ERROR:",
            e,
            flush=True
        )


        return None





# ==========================
# ОБРАБОТКА СООБЩЕНИЙ
# ==========================

def process_updates():

    global offset


    print(
        "CHECKING TELEGRAM UPDATES",
        flush=True
    )


    data = get_updates()



    for update in data.get(
        "result",
        []
    ):


        offset = update["update_id"] + 1



        message = update.get(
            "message"
        )


        if not message:

            continue



        # ==========================
        # ПРОВЕРКА АДМИНА
        # ==========================

        user_id = message["from"]["id"]



        if user_id not in ADMIN_IDS:


            print(

                "UNAUTHORIZED USER:",

                user_id,

                flush=True

            )


            continue




        photo = message.get(
            "photo"
        )



        if not photo:


            print(

                "MESSAGE WITHOUT PHOTO SKIPPED",

                flush=True

            )


            continue




        caption = message.get(
            "caption",
            ""
        )



        product = caption or "Товар"



        file_id = photo[-1]["file_id"]



        image_url = get_file_url(
            file_id
        )



        print(

            "NEW POST:",

            product,

            flush=True

        )


        print(

            "IMAGE URL:",

            image_url,

            flush=True

        )




        try:


            result = send_post(

                product=product,

                image_url=image_url

            )


            print(

                "POST RESULT:",

                result,

                flush=True

            )



        except Exception as e:


            print(

                "SEND POST ERROR:",

                e,

                flush=True

            )






# ==========================
# ЗАПУСК
# ==========================

def start_listener():


    print(

        "STARTING TELEGRAM LISTENER",

        flush=True

    )



    while True:


        try:

            process_updates()



        except Exception as e:


            print(

                "LISTENER ERROR:",

                e,

                flush=True

            )



        time.sleep(2)
