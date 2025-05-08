from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, tags=['Orders'], prefix="/api/orders")


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB order"}
