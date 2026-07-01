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
