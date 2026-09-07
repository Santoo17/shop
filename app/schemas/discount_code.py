from pydantic import BaseModel, ConfigDict, Field


class DiscountCodeCreate(BaseModel):
    codice: str
    percentuale: int = Field(ge=5, le=25, description="La percentuale di sconto deve essere compresa tra 5 e 25")
    attivo: bool = True


class DiscountCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codice: str
    percentuale: int
    attivo: bool

class DiscountCodeUpdate(BaseModel):
    codice: str | None = None
    percentuale: int | None = Field(None, ge=5, le=25, description="La percentuale di sconto deve essere compresa tra 5 e 25")
    attivo: bool | None = None