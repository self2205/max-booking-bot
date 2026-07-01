from sqlalchemy import Column, Integer, String
from database import Base


class BookingDB(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String)
    name = Column(String)
    phone = Column(String)
