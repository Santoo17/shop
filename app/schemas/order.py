from pydantic import BaseModel, ConfigDict

class CheckoutItem(BaseModel):
    product_id: int
    quantita: int

class CheckoutRequest(BaseModel):
    items: list[CheckoutItem]
    codice_sconto: str | None = None

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantita: int
    prezzo_unitario: float

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    totale: float
    stato: str
    codice_sconto: str | None
    items: list[OrderItemRead]

class OrderStatusUpdate(BaseModel):
    stato: str