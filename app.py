from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from routers.max_webhook import router as max_router
from routers.telegram_webhook import router as telegram_router

from telegram_listener import start_listener
from telegram_admin_listener import start_admin_listener

import secrets
import base64
import json
import threading


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
    clear_state,
    WAIT_MANAGER_MESSAGE
)


app = FastAPI()



# ==========================
# START TELEGRAM LISTENERS
# ==========================

@app.on_event("startup")
def startup_event():


    print(
        "🔥 STARTING TELEGRAM SERVICES",
        flush=True
    )



    # ==========================
    # ПОСТИНГ ТОВАРОВ
    # TG_POST_TOKEN
    # ==========================

    try:


        post_thread = threading.Thread(

            target=start_listener,

            daemon=True

        )


        post_thread.start()


        print(
            "✅ POST LISTENER STARTED",
            flush=True
        )


    except Exception as e:


        print(
            "❌ POST LISTENER ERROR:",
            e,
            flush=True
        )




    # ==========================
    # ОБРАБОТКА ЗАЯВОК
    # TG_TOKEN
    # ==========================

    try:


        admin_thread = threading.Thread(

            target=start_admin_listener,

            daemon=True

        )


        admin_thread.start()


        print(
            "✅ ADMIN LISTENER STARTED",
            flush=True
        )


    except Exception as e:


        print(
            "❌ ADMIN LISTENER ERROR:",
            e,
            flush=True
        )



    print(
        "🔥 TELEGRAM SERVICES RUNNING",
        flush=True
    )

# ==========================
# ROUTERS
# ==========================

app.include_router(max_router)

app.include_router(telegram_router)



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
