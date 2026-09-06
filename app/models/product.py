from app.models.base import Base
from sqlalchemy import BigInteger, Float, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    from app.models.review import Review

class Product(Base):
    __tablename__="products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descrizione: Mapped[str | None] = mapped_column(Text, nullable=True)
    prezzo: Mapped[float] = mapped_column(Float, nullable=False)
    giacenza: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valutazione_media: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")