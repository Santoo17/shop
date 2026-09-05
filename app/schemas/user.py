from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserCreate(BaseModel):
    nome: str
    cognome: str
    email: EmailStr
    password: str
    indirizzo: str | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    cognome: str
    email: EmailStr
    ruolo: str
    indirizzo: str | None
    saldo: float

class UserUpdate(BaseModel):
    nome: str | None = None
    cognome: str | None = None
    indirizzo: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class AdminUpdate(BaseModel):
    nome: str | None = None
    cognome: str | None = None
    indirizzo: str | None = None
    saldo: float | None = Field(default=None, ge=0.0, description="Il saldo non può essere negativo")