import time
import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post_album


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None

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


        message = update.get("message")


        if not message:
            continue



        photo = message.get("photo")


        if not photo:
            continue



        caption = message.get(
            "caption",
            "Товар"
        )


        file_id = photo[-1]["file_id"]



        media_group_id = message.get(
            "media_group_id"
        )



        # ==========================
        # ЕСЛИ ЭТО АЛЬБОМ
        # ==========================

        if media_group_id:


            if media_group_id not in albums:

                albums[media_group_id] = {
                    "photos": [],
                    "caption": caption
                }


            albums[media_group_id]["photos"].append(
                file_id
            )


            print(
                "ADD PHOTO TO ALBUM",
                media_group_id
            )


        else:


            send_post_album(

                product=caption,

                photos=[file_id]

            )



    # отправляем накопленные альбомы

    send_albums()



def send_albums():


    global albums


    for album_id in list(albums.keys()):


        album = albums[album_id]


        # ждём пока Telegram пришлёт все фото

        if len(album["photos"]) < 2:
            continue



        send_post_album(

            product=album["caption"],

            photos=album["photos"]

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


    time.sleep(3)
