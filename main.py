from fastapi import FastAPI
from app.routers import auth, products, users, orders, reviews

app = FastAPI(title="Bazar")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(reviews.router)


@app.get("/")
def read_root():
    return {"message": "Il server è attivo!"}