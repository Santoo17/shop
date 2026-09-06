from app.models.base import Base
from sqlalchemy import BigInteger, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.review import Review
class UserRole(str, enum.Enum):
    STANDARD = "standard"
    ADMIN = "admin"

class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    cognome: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    ruolo: Mapped[UserRole]
    password_digest: Mapped[str] = mapped_column(String(255), nullable=False)
    indirizzo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    saldo: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")