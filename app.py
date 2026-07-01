from fastapi import FastAPI
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
    print(f"Товар: {data.product}")
    print(f"Имя: {data.name}")
    print(f"Телефон: {data.phone}")
    print("==========================")

    return {
        "success": True
    }
