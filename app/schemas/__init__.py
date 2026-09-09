from app.schemas.user import UserRead, UserCreate, UserUpdate, Token, AdminUpdate, AdminAddSaldo
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate, ProductAddGiacenza
from app.schemas.order import (
    CheckoutItem,
    CheckoutRequest,
    OrderItemRead,
    OrderRead,
    OrderStatusUpdate
)

from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.schemas.discount_code import DiscountCodeRead, DiscountCodeCreate, DiscountCodeUpdate