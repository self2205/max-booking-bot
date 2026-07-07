import time
import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None


# хранилище альбомов
albums = {}



def get_updates():

    global offset


    params = {
        "timeout": 30
    }


    if offset:
        params["offset"] = offset



    r = requests.get(

        f"{API_URL}/getUpdates",

        params=params,

        timeout=35

    )


    return r.json()




def process_updates():

    global offset


    data = get_updates()



    for update in data.get("result", []):


        offset = update["update_id"] + 1



        message = update.get(
            "message"
        )


        if not message:
            continue



        photo = message.get(
            "photo"
        )


        if not photo:
            continue



        caption = message.get(
            "caption",
            ""
        )


        media_group_id = message.get(
            "media_group_id"
        )



        file_id = photo[-1]["file_id"]



        # ==========================
        # АЛЬБОМ
        # ==========================

        if media_group_id:


            if media_group_id not in albums:

                albums[media_group_id] = {

                    "photos": [],

                    "caption": caption or "Товар",

                    "time": time.time()

                }



            albums[media_group_id]["photos"].append(
                file_id
            )



            print(
                "ADD PHOTO TO ALBUM:",
                media_group_id
            )



        else:


            print(
                "NEW SINGLE POST:",
                caption
            )


            send_post(

                product=caption or "Товар",

                image_url=file_id

            )




    # ==========================
    # ОТПРАВКА СОБРАННЫХ АЛЬБОМОВ
    # ==========================


    now = time.time()



    for album_id in list(albums.keys()):


        album = albums[album_id]



        # ждем пока придут все фото

        if now - album["time"] < 2:

            continue



        print(
            "NEW ALBUM POST:",
            album["caption"],
            "PHOTOS:",
            len(album["photos"])
        )



        send_post(

            product=album["caption"],

            image_url=album["photos"]

        )



        del albums[album_id]





while True:


    try:

        process_updates()


    except Exception as e:

        print(
            "ERROR:",
            e
        )


    time.sleep(2)
