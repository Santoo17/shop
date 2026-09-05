from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    nome: str
    descrizione: str | None = None
    prezzo: float
    giacenza: int

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    descrizione: str | None
    prezzo: float
    giacenza: int

class ProductUpdate(BaseModel):
    nome: str | None = None
    descrizione: str | None = None
    prezzo: float | None = None
    giacenza: int | None = None