from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

import secrets
import requests
import urllib.parse
import json
import base64


from config import *
from database import init_db, get_bookings
from booking_service import create_booking
from max_service import send_message_max, extract_image_from_webhook
from states import get_state, set_state, clear_state


app = FastAPI()

init_db()


security = HTTPBasic()


# ==========================
# ADMIN AUTH
# ==========================

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):

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
            },
        )


    return True



# ==========================
# ENCODE / DECODE PRODUCT
# ==========================

def encode_product(product):

    encoded = base64.b64encode(
        product.encode("utf-8")
    ).decode("utf-8")


    return "p_" + encoded



def decode_product(payload):

    try:

        if payload.startswith("p_"):
            payload = payload[2:]


        decoded = base64.b64decode(
            payload
        ).decode("utf-8")


        return decoded


    except Exception as e:

        print(
            "DECODE ERROR:",
            e
        )

        return None



# ==========================
# CLEAN PRODUCT
# ==========================

def extract_product(text):

    if not text:
        return None


    text = str(text).strip()


    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


    return "\n".join(lines)





# ==========================
# MODEL
# ==========================

class Booking(BaseModel):

    product: str
    name: str
    phone: str



# ==========================
# HOME
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


    print("\n========== MAX WEBHOOK ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=================================\n")



    update_type = data.get("update_type")



    # ==================================
    # BOT STARTED (НАЖАТИЕ КНОПКИ)
    # ==================================

    if update_type == "bot_started":


        user_id = data.get("user_id")

        chat_id = data.get("chat_id")

        payload = data.get("payload", "")



        print(
            "RAW PAYLOAD:",
            payload
        )



        product = None



        # новая система p_ BASE64

        if payload.startswith("p_"):

            product = decode_product(payload)



        # старый вариант product_

        elif payload.startswith("product_"):

            product = payload.replace(
                "product_",
                "",
                1
            )



        else:

            product = payload



        product = extract_product(product)



        print(
            "FINAL PRODUCT:",
            product
        )



        if product:



            set_state(
                user_id,
                "WAIT_NAME",
                {
                    "product": product
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
                """
👋 Привет!

Что хотите забронировать?
"""
            )



        return {
            "ok": True
        }






    # ==================================
    # MESSAGE CREATED
    # ==================================

    if update_type != "message_created":

        return {
            "ok": True
        }



    message = data.get(
        "message",
        {}
    )



    chat_id = (
        message
        .get("recipient", {})
        .get("chat_id")
    )


    user_id = (
        message
        .get("sender", {})
        .get("user_id")
    )



    body = message.get(
        "body",
        {}
    )



    text = body.get(
        "text",
        ""
    ).strip()



    if not chat_id:

        return {
            "ok": True
        }




    state = get_state(user_id)





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
            """
👋 Привет!

Что хотите забронировать?
"""
        )


        return {
            "ok": True
        }






    # ==========================
    # PRODUCT
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
    # NAME
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
            "📞 Введите телефон"
        )


        return {
            "ok": True
        }







    # ==========================
    # PHONE
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



        clear_state(user_id)



        send_message_max(
            chat_id,
            f"""
✅ Заявка создана!

ID: {booking_id}
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


    print("\n========== TELEGRAM ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("==============================\n")



    message = data.get("message")


    if not message:

        return {
            "ok": True
        }



    chat = message.get(
        "chat",
        {}
    )


    chat_id = chat.get(
        "id"
    )



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




    # ==========================
    # СОБИРАЕМ ТОВАР
    # ==========================

    product_raw = (
        caption
        if caption
        else text
    )



    product = extract_product(
        product_raw
    )



    if not product:

        product = "Товар"



    print(
        "POST PRODUCT:",
        product
    )




    # ==========================
    # КОДИРУЕМ ДЛЯ MAX
    # ==========================

    encoded = encode_product(
        product
    )



    product_url = (
        "https://max.ru/se13456903_bot"
        "?start="
        + encoded
    )




    reply_markup = json.dumps({

        "inline_keyboard": [

            [

                {
                    "text": "🟢 Забронировать",

                    "url": product_url
                }

            ]

        ]

    })





    try:


        # ==========================
        # ЕСЛИ ЕСТЬ ФОТО
        # ==========================

        if photo:


            file_id = photo[-1]["file_id"]



            resp = requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",

                data={

                    "chat_id":
                    TG_CHANNEL_CHAT_ID,


                    "photo":
                    file_id,


                    "caption":
                    product,


                    "reply_markup":
                    reply_markup

                },

                timeout=15

            )




        # ==========================
        # ЕСЛИ ТОЛЬКО ТЕКСТ
        # ==========================

        else:


            resp = requests.post(

                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",

                data={

                    "chat_id":
                    TG_CHANNEL_CHAT_ID,


                    "text":
                    product,


                    "reply_markup":
                    reply_markup

                },

                timeout=15

            )




        print(
            "TG STATUS:",
            resp.status_code
        )

        print(
            resp.text
        )




    except Exception as e:


        print(
            "TELEGRAM ERROR:",
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

    padding:12px;

    text-align:left;

}


td {

    border:1px solid #ddd;

    padding:10px;

}


</style>


</head>



<body>



<h2>
📋 Заявки магазина
</h2>



<table>


<tr>

<th>ID</th>

<th>Товар</th>

<th>Имя</th>

<th>Телефон</th>

<th>Фото</th>

<th>Статус</th>

<th>Дата</th>

</tr>

"""



    for row in rows:


        photo = "-"



        if row.get("image_url"):


            photo = f"""

<a href="{row['image_url']}" target="_blank">

<img src="{row['image_url']}" width="100">

</a>

"""



        html += f"""

<tr>


<td>
{row['id']}
</td>


<td>
{row['product']}
</td>


<td>
{row['name']}
</td>


<td>
{row['phone']}
</td>


<td>
{photo}
</td>


<td>
{row['status']}
</td>


<td>
{row['created_at']}
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
