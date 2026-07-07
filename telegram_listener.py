import time
import requests

from config import TG_POST_TOKEN
from telegram_poster import send_post


API_URL = f"https://api.telegram.org/bot{TG_POST_TOKEN}"


offset = None


# хранение альбомов
albums = {}



# ==================================
# GET UPDATES
# ==================================

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





# ==================================
# ОБРАБОТКА UPDATE
# ==================================

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



        file_id = photo[-1]["file_id"]



        caption = message.get(
            "caption"
        )


        if not caption:

            caption = "Товар"



        media_group_id = message.get(
            "media_group_id"
        )



        # ==================================
        # АЛЬБОМ
        # ==================================

        if media_group_id:


            if media_group_id not in albums:


                albums[media_group_id] = {


                    # все фото для канала

                    "photos": [],


                    # первое фото для базы

                    "preview": file_id,


                    "caption": caption,


                    "time": time.time()

                }



            # добавляем фото в альбом

            if file_id not in albums[media_group_id]["photos"]:


                albums[media_group_id]["photos"].append(
                    file_id
                )



            albums[media_group_id]["time"] = time.time()



            print(

                "ADD ALBUM PHOTO:",

                media_group_id,

                len(
                    albums[media_group_id]["photos"]
                ),

                flush=True

            )



            continue





        # ==================================
        # ОДИНОЧНОЕ ФОТО
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







# ==================================
# ОТПРАВКА АЛЬБОМА
# ==================================

def send_albums():


    now = time.time()



    for album_id in list(albums.keys()):


        album = albums[album_id]



        # ждём пока Telegram пришлёт все фото

        if now - album["time"] < 5:


            continue





        print(

            "SEND ALBUM:",

            album["caption"],

            "COUNT:",

            len(album["photos"]),

            flush=True

        )



        send_post(

            product=album["caption"],

            image_url=album["photos"],

            preview_image=album["preview"]

        )



        del albums[album_id]







# ==================================
# START LISTENER
# ==================================

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
