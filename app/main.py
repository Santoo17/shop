from fastapi import FastAPI
from app.routers import auth, products

app = FastAPI(title="Bazar")
app.include_router(auth.router)
app.include_router(products.router)