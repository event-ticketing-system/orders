import asyncio
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders
from app.consumer import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, tags=['Orders'], prefix="/api/orders")


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB order"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_events()) 

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("./index.html", "r") as file:
        return file.read()