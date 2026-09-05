from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas import CheckoutRequest, OrderRead
from app.auth import get_current_user
from app.services.checkout import checkout, RigaCarrello

router = APIRouter(tags=["orders"])


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def effettua_checkout(
    dati: CheckoutRequest,
    db: Session = Depends(get_db),
    utente: User = Depends(get_current_user),
):
    carrello = [RigaCarrello(product_id=item.product_id, quantita=item.quantita) for item in dati.items]
    try:
        ordine = checkout(db, utente, carrello, dati.codice_sconto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ordine