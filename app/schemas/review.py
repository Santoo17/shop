from pydantic import BaseModel, ConfigDict, Field

class ReviewCreate(BaseModel):
    commento: str | None = None
    valutazione: int = Field(..., ge=1, le=5, description="Valutazione da 1 a 5")

class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    commento: str | None
    valutazione: int
    user_id: int
    product_id: int

class ReviewUpdate(BaseModel):
    commento: str | None = None
    valutazione: int | None = Field(None, ge=1, le=5, description="Valutazione da 1 a 5")
    