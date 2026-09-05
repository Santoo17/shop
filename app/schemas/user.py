from pydantic import BaseModel, EmailStr, ConfigDict

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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    nome: str | None = None
    cognome: str | None = None
    indirizzo: str | None = None