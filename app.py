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
async def booking(data: Booking):

    print("\n========== НОВАЯ ЗАЯВКА ==========")
    print(f"Товар: {data.product}")
    print(f"Имя: {data.name}")
    print(f"Телефон: {data.phone}")
    print("==================================\n")

    return {
        "success": True,
        "message": "Заявка получена"
    }


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("\n========== WEBHOOK ==========")
    print(data)
    print("=============================\n")

    return {"ok": True}
