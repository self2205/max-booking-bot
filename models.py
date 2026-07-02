from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    product = Column(String)

    name = Column(String)

    phone = Column(String)

    status = Column(
        String,
        default="🟢 Новая"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
