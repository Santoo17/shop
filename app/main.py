from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Bazar")
app.include_router(auth.router)