import aio_pika
import asyncio
import json
import os
from app.routes.orders import publish_event
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Order
from app.database import Base
from app.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL
from sqlalchemy.exc import SQLAlchemyError

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def handle_payment_completed(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            order_id = payload["order_id"]

            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = "complete"
                db.commit()
                print(f"[order] Payment confirmed for order {order_id}")
                await publish_event("order_completed", {
                    "event_id": order.event_id,
                    "quantity": order.quantity
                })
            else:
                print(f"[order] Order ID {order_id} not found")

        except (json.JSONDecodeError, KeyError, SQLAlchemyError) as e:
            print(f"[order] Failed to process payment_completed message: {e}")

async def consume_events():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            break
        except Exception as e:
            print("Waiting for RabbitMQ to be ready...")
            await asyncio.sleep(5)

    channel = await connection.channel()
    exchange = await channel.declare_exchange("order_events", aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("", exclusive=True)
    await queue.bind(exchange, routing_key="payment_completed")

    print("[order] Waiting for payment_completed events...")
    await queue.consume(handle_payment_completed)
