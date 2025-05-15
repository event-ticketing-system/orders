from pydantic import BaseModel
from datetime import datetime

class OrderCreate(BaseModel):
    event_id: str
    event_name: str
    quantity: int
    price: float
    total_price: float
    order_time: datetime
    user_id: str

class OrderResponse(OrderCreate):
    id: int
    status: str

    class Config:
        orm_mode = True