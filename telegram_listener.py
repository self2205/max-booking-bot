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



        # ==================================
        # АЛЬБОМ
        # ==================================

        if media_group_id:


            if media_group_id not in albums:


                albums[media_group_id] = {

                    "photos": [],

                    "caption": caption,

                    "time": time.time()

                }



            albums[media_group_id]["photos"].append(
                file_id
            )


            albums[media_group_id]["time"] = time.time()



            print(

                "ADD PHOTO TO ALBUM:",

                media_group_id,

                len(
                    albums[media_group_id]["photos"]
                ),

                flush=True

            )


            continue





        # ==================================
        # ОДНО ФОТО
        # ==================================

        print(

            "NEW SINGLE POST:",

            caption,

            flush=True

        )


        send_post(

            product=caption,

            image_url=file_id

        )




    send_albums()






def send_albums():


    now = time.time()



    for album_id in list(albums.keys()):


        album = albums[album_id]



        # ждём пока придут все фото

        if now - album["time"] < 2:


            continue




        print(

            "SEND ALBUM:",

            album["caption"],

            "PHOTOS:",

            len(album["photos"]),

            flush=True

        )



        send_post(

            product=album["caption"],

            image_url=album["photos"]

        )



        del albums[album_id]




def start_listener():

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
