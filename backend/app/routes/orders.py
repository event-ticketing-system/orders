from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import SessionLocal
import aio_pika
import json
import asyncio
import os

router = APIRouter()
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/orders")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    message = {
        "order_id": db_order.id,
        "event_id": db_order.event_id,
        "event_name": db_order.event_name,
        "quantity": db_order.quantity,
        "price": db_order.price,
        "total_price": db_order.total_price,
        "order_time": db_order.order_time.isoformat(),
    }

    # Fire-and-forget async RabbitMQ publish
    asyncio.create_task(publish_event("order_created", message))

    return {"message": "Order received", "order_id": db_order.id}

async def publish_event(routing_key: str, payload: dict):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("order_events", aio_pika.ExchangeType.TOPIC)
        await exchange.publish(
            aio_pika.Message(body=json.dumps(payload).encode()),
            routing_key=routing_key,
        )
