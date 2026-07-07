import time
import requests

from config import (
    TG_POST_TOKEN,
    TG_TOKEN,
    ADMIN_IDS
)

from telegram_poster import send_post


POST_API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"



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

            f"{POST_API_URL}/getUpdates",

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
# ПЕРЕНОС ФОТО НА ВТОРОГО БОТА
# ==========================

def transfer_photo(file_id):

    try:


        # получаем путь файла у TG_POST_TOKEN

        file_info = requests.get(

            f"{POST_API_URL}/getFile",

            params={
                "file_id": file_id
            },

            timeout=15

        ).json()



        if not file_info.get("ok"):


            print(
                "GET FILE ERROR:",
                file_info,
                flush=True
            )


            return None




        file_path = file_info["result"]["file_path"]




        # скачиваем фото первым ботом

        photo_response = requests.get(

            f"https://api.telegram.org/file/bot{TG_POST_TOKEN}/{file_path}",

            timeout=30

        )



        photo_response.raise_for_status()



        photo_bytes = photo_response.content





        # отправляем фото второму боту

        upload = requests.post(

            f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",

            data={

                "chat_id": ADMIN_IDS[0]

            },

            files={

                "photo": photo_bytes

            },

            timeout=30

        ).json()





        if not upload.get("ok"):


            print(

                "UPLOAD PHOTO ERROR:",

                upload,

                flush=True

            )


            return None





        new_file_id = upload["result"]["photo"][-1]["file_id"]



        print(

            "NEW FILE ID:",

            new_file_id,

            flush=True

        )



        return new_file_id




    except Exception as e:


        print(

            "TRANSFER PHOTO ERROR:",

            e,

            flush=True

        )


        return None






# ==========================
# ОБРАБОТКА ПОСТОВ
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

                "MESSAGE WITHOUT PHOTO",

                flush=True

            )


            continue





        caption = message.get(

            "caption",

            ""

        )



        product = caption or "Товар"




        old_file_id = photo[-1]["file_id"]





        print(

            "OLD FILE ID:",

            old_file_id,

            flush=True

        )





        new_file_id = transfer_photo(

            old_file_id

        )




        if not new_file_id:


            print(

                "PHOTO TRANSFER FAILED",

                flush=True

            )


            continue





        print(

            "NEW POST:",

            product,

            flush=True

        )





        try:



            result = send_post(

                product=product,

                image_url=new_file_id

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
# START
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
