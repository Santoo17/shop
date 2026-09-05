from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProductCreate(BaseModel):
    nome: str
    descrizione: str | None = None
    prezzo: float 
    giacenza: int 

    @field_validator("prezzo")
    @classmethod
    def valida_prezzo(cls, valore):
        if valore <= 0:
            raise ValueError("Il prezzo deve essere maggiore di zero")
        return valore

    @field_validator("giacenza")
    @classmethod
    def valida_giacenza(cls, valore):
        if valore < 0:
            raise ValueError("La giacenza non può essere negativa")
        return valore
    
    

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

    @field_validator("prezzo")
    @classmethod
    def valida_prezzo(cls, valore):
        if valore is not None and valore <= 0:
            raise ValueError("Il prezzo deve essere maggiore di zero")
        return valore

    @field_validator("giacenza")
    @classmethod
    def valida_giacenza(cls, valore):
        if valore is not None and valore < 0:
            raise ValueError("La giacenza non può essere negativa")
        return valore