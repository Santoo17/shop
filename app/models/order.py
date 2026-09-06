from app.models.base import Base
from sqlalchemy import BigInteger, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order_item import OrderItem

class OrderStatus(str, enum.Enum):
    CONFERMATO = "Confermato"
    SPEDITO = "Spedito"
    CONSEGNATO = "Consegnato"
    ANNULLATO = "Annullato"
    RIMBORSATO = "Rimborsato"

class Order(Base):
    __tablename__="orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    totale: Mapped[float] = mapped_column(Float, nullable=False)
    stato: Mapped[OrderStatus]
    codice_sconto: Mapped[str | None] = mapped_column(String(30), nullable=True)
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    