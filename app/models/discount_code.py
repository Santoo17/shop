from app.models.base import Base
from sqlalchemy import BigInteger, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class DiscountCode(Base):
    __tablename__="discount_codes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codice: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    percentuale: Mapped[int] = mapped_column(Integer, nullable=False)
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)