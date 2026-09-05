from fastapi import FastAPI
from app.routers import auth, products, users, orders

app = FastAPI(title="Bazar")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)