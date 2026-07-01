from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


class Booking(BaseModel):
    product: str
    name: str
    phone: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "MAX Booking Bot"
    }


@app.post("/booking")
def booking(data: Booking):

    print("====== НОВАЯ ЗАЯВКА ======")
    print(data)
    print("==========================")

    return {"success": True}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("========== СОБЫТИЕ MAX ==========")
    print(data)
    print("=================================")

    return {"ok": True}
import os
import requests

MAX_TOKEN = os.getenv("MAX_TOKEN")
MAX_SECRET = os.getenv("MAX_SECRET")


@app.get("/setup")
def setup():

    headers = {
        "Authorization": MAX_TOKEN,
        "Content-Type": "application/json"
    }

    body = {
        "url": "https://max-booking-bot-k3dx.onrender.com/webhook",
        "update_types": [
            "message_created",
            "bot_added",
            "bot_started"
        ],
        "secret": MAX_SECRET
    }

    r = requests.post(
        "https://platform-api2.max.ru/subscriptions",
        headers=headers,
        json=body
    )

    return r.json()
