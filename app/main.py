from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products, users, orders, reviews, discounts

app = FastAPI(title="Bazar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(discounts.router)


@app.get("/")
def read_root():
    return {"message": "Il server è attivo!"}