from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from routers.max_webhook import router as max_router

import secrets
import base64
import json
import requests



from config import *

from database import (
    init_db,
    get_bookings,
    get_product
)

from booking_service import create_booking

from max_service import send_message_max

from states import (
    get_state,
    set_state,
    clear_state
)


app = FastAPI()


# ==========================
# DATABASE INIT
# ==========================

init_db()



# ==========================
# PAYLOAD ENCODER
# ==========================

def encode_payload(data: dict):

    raw = json.dumps(
        data,
        ensure_ascii=False
    )

    return base64.urlsafe_b64encode(
        raw.encode("utf-8")
    ).decode("utf-8")



def decode_payload(payload: str):

    try:

        raw = base64.urlsafe_b64decode(
            payload.encode("utf-8")
        )

        return json.loads(
            raw.decode("utf-8")
        )

    except Exception as e:

        print(
            "PAYLOAD ERROR:",
            e
        )

        return {}

# ==========================
# ADMIN AUTH
# ==========================

security = HTTPBasic()


def check_auth(
    credentials: HTTPBasicCredentials = Depends(security)
):

    login_ok = secrets.compare_digest(
        credentials.username,
        ADMIN_LOGIN
    )

    password_ok = secrets.compare_digest(
        credentials.password,
        ADMIN_PASSWORD
    )


    if not (login_ok and password_ok):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong login",
            headers={
                "WWW-Authenticate": "Basic"
            }
        )


    return True



# ==========================
# BOOKING MODEL
# ==========================

class Booking(BaseModel):

    product: str
    name: str
    phone: str



# ==========================
# ROOT
# ==========================

@app.get("/")
def root():

    return {
        "status": "ok",
        "service": "MAX Booking Bot"
    }



# ==========================
# MANUAL BOOKING API
# ==========================

@app.post("/booking")
def booking(data: Booking):

    booking_id = create_booking(
        product=data.product,
        name=data.name,
        phone=data.phone
    )


    return {
        "success": True,
        "booking_id": booking_id
    }
# ==========================
# MAX WEBHOOK
# ==========================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("ALL KEYS:", data.keys())
    print("FULL DATA:", data)


    print("\n========== MAX WEBHOOK ==========")
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )
    print("=================================\n")



    update_type = data.get(
        "update_type"
    )



    # ==========================
    # ЧЕЛОВЕК ОТКРЫЛ БОТА ПО КНОПКЕ
    # ==========================

    if update_type == "bot_started":


        user_id = data.get(
            "user_id"
        )


        chat_id = data.get(
            "chat_id"
        )


        payload = (
        data.get("payload")
        or data.get("start")
        or data.get("parameter")
        or ""
        )


        print(
            "RAW PAYLOAD:",
            payload
        )


        product_data = get_product(
            payload
        )


        if product_data:

            product = product_data["product"]

            image_url = product_data["image_url"]

        else:

            product = None

            image_url = None

        print(
            "PRODUCT:",
            product
        )


        print(
            "IMAGE:",
            image_url
        )



        if product:


            set_state(
                user_id,
                "WAIT_NAME",
                {
                    "product": product,
                    "image_url": image_url
                }
            )


            send_message_max(
                chat_id,
                f"""
🟢 Бронирование

📦 {product}

✍️ Введите ваше имя
"""
            )


        else:


            set_state(
                user_id,
                "WAIT_PRODUCT",
                {}
            )


            send_message_max(
                chat_id,
                "👋 Привет!\n\nЧто хотите забронировать?"
            )


        return {
            "ok": True
        }




    # ==========================
    # НЕ СООБЩЕНИЕ
    # ==========================

    if update_type != "message_created":

        return {
            "ok": True
        }




    message = data.get(
        "message",
        {}
    )



    chat_id = message.get(
        "recipient",
        {}
    ).get(
        "chat_id"
    )



    user_id = message.get(
        "sender",
        {}
    ).get(
        "user_id"
    )



    text = message.get(
        "body",
        {}
    ).get(
        "text",
        ""
    )



    if not chat_id:

        return {
            "ok": True
        }



    state = get_state(
        user_id
    )



    # ==========================
    # START
    # ==========================

    if text == "/start":


        set_state(
            user_id,
            "WAIT_PRODUCT",
            {}
        )


        send_message_max(
            chat_id,
            "👋 Привет!\n\nЧто хотите забронировать?"
        )


        return {
            "ok": True
        }




    # ==========================
    # ТОВАР
    # ==========================

    if state and state["state"] == "WAIT_PRODUCT":


        state["data"]["product"] = text


        set_state(
            user_id,
            "WAIT_NAME",
            state["data"]
        )


        send_message_max(
            chat_id,
            "✍️ Введите ваше имя"
        )


        return {
            "ok": True
        }




    # ==========================
    # ИМЯ
    # ==========================

    if state and state["state"] == "WAIT_NAME":


        state["data"]["name"] = text


        set_state(
            user_id,
            "WAIT_PHONE",
            state["data"]
        )


        send_message_max(
            chat_id,
            "📞 Введите ваш телефон"
        )


        return {
            "ok": True
        }




    # ==========================
    # ТЕЛЕФОН
    # ==========================

    if state and state["state"] == "WAIT_PHONE":


        state["data"]["phone"] = text



        booking_id = create_booking(

            product=state["data"].get(
                "product"
            ),

            name=state["data"].get(
                "name"
            ),

            phone=state["data"].get(
                "phone"
            ),

            image_url=state["data"].get(
                "image_url"
            )
        )



        clear_state(
            user_id
        )



        send_message_max(
            chat_id,
            f"""
✅ Заявка создана!

Номер:
#{booking_id}
"""
        )


        return {
            "ok": True
        }



    return {
        "ok": True
    }
    # ==========================
# TELEGRAM WEBHOOK
# ==========================

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):


    data = await request.json()


    message = data.get(
        "message"
    )


    if not message:

        return {
            "ok": True
        }



    text = message.get(
        "text",
        ""
    )


    caption = message.get(
        "caption",
        ""
    )


    photo = message.get(
        "photo"
    )



    product = (
        caption
        if caption
        else text
    )



    if not product:

        product = "Товар"



    # ==========================
    # ПОЛУЧАЕМ ФОТО
    # ==========================

    image_url = None



    if photo:


        try:


            file_id = photo[-1].get(
                "file_id"
            )



            response = requests.get(

                f"https://api.telegram.org/bot{TG_TOKEN}/getFile",

                params={
                    "file_id": file_id
                },

                timeout=10

            )



            result = response.json()



            file_path = result["result"]["file_path"]



            image_url = (
                f"https://api.telegram.org/file/"
                f"bot{TG_TOKEN}/{file_path}"
            )



        except Exception as e:


            print(
                "PHOTO ERROR:",
                e
            )




    # ==========================
    # PAYLOAD ДЛЯ MAX
    # ==========================

    payload = encode_payload(
        {
            "product": product,
            "image_url": image_url
        }
    )



    max_url = (

        "https://max.ru/"
        "se13456903_bot"
        "?start="
        + payload

    )



    reply_markup = {


        "inline_keyboard": [

            [

                {

                    "text": "🟢 Забронировать",

                    "url": max_url

                }

            ]

        ]

    }




    # ==========================
    # ОТПРАВКА В КАНАЛ
    # ==========================

    try:


        if image_url:


            requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "photo": image_url,

                    "caption": f"📦 {product}",

                    "reply_markup": reply_markup

                },

                timeout=15

            )


        else:


            requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                json={

                    "chat_id": TG_CHANNEL_CHAT_ID,

                    "text": f"📦 {product}",

                    "reply_markup": reply_markup

                },

                timeout=15

            )



    except Exception as e:


        print(
            "CHANNEL ERROR:",
            e
        )



    return {
        "ok": True
    }
    # ==========================
# ADMIN PANEL
# ==========================

@app.get(
    "/admin",
    response_class=HTMLResponse
)
def admin(
    auth: bool = Depends(check_auth)
):


    rows = get_bookings()



    html = """

<!DOCTYPE html>

<html lang="ru">

<head>

<meta charset="UTF-8">

<title>Заявки</title>


<style>

body {

    font-family: Arial;

    background:#f5f5f5;

    margin:40px;

}


table {

    width:100%;

    border-collapse:collapse;

    background:white;

}


th {

    background:#222;

    color:white;

    padding:10px;

}


td {

    border:1px solid #ddd;

    padding:10px;

}


img {

    width:100px;

    border-radius:8px;

}

</style>


</head>


<body>


<h2>
📋 Заявки на бронирование
</h2>



<table>


<tr>

<th>ID</th>

<th>Фото</th>

<th>Товар</th>

<th>Имя</th>

<th>Телефон</th>

<th>Статус</th>

<th>Дата</th>

</tr>

"""



    for row in rows:


        photo = "—"



        image = row.get(
            "image_url"
        )



        if image:


            photo = f"""

<a href="{image}" target="_blank">

<img src="{image}">

</a>

"""



        html += f"""

<tr>

<td>
{row.get('id','')}
</td>


<td>
{photo}
</td>


<td>
{row.get('product','')}
</td>


<td>
{row.get('name','')}
</td>


<td>
{row.get('phone','')}
</td>


<td>
{row.get('status','')}
</td>


<td>
{row.get('created_at','')}
</td>


</tr>

"""



    html += """

</table>


</body>

</html>

"""



    return HTMLResponse(
        content=html
    )
