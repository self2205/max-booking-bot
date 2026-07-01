from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

MAX_TOKEN = os.getenv("MAX_TOKEN")


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


@app.get("/updates")
def updates():
    headers = {
        "Authorization": f"Bearer {MAX_TOKEN}"
    }

    r = requests.get(
        "https://botapi.max.ru/updates",
        headers=headers
    )

    return r.json()


@app.post("/booking")
def booking(data: Booking):

    print(data)

    return {
        "success": True
    }
from fastapi import Request

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("========== MAX EVENT ==========")
    print(data)
    print("===============================")

    return {"ok": True}
