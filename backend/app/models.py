from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending")
    order_time = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(String, nullable=False)
    merchant_transaction_id = Column(String, nullable=False)