from app.models.base import Base
from sqlalchemy import BigInteger, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product

class OrderItem(Base):
    __tablename__="order_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantita: Mapped[int] = mapped_column(Integer, nullable=False)
    prezzo_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
