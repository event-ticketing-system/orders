from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, tags=['Orders'], prefix="/api/orders")


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB order"}
