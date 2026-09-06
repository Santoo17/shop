from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models import User, UserRole, Order, OrderStatus
from app.schemas import CheckoutRequest, OrderRead, OrderStatusUpdate
from app.auth import get_current_user, require_admin_user
from app.services.checkout import checkout, RigaCarrello
from app.services import cambia_stato_ordine, richiedi_rimborso

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

@router.get("/orders", response_model=list[OrderRead])
def lista_ordini(
    db: Session = Depends(get_db),
    utente: User = Depends(get_current_user),
):
    if utente.ruolo == UserRole.ADMIN:
        query = select(Order)
    else:
        query = select(Order).where(Order.user_id == utente.id)
    ordini = db.execute(query).scalars().all()
    return ordini

@router.get("/orders/{order_id}", response_model=OrderRead)
def dettaglio_ordine(order_id: int, db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    if utente.ruolo == UserRole.ADMIN:
        ordine = db.get(Order, order_id)
    else:
        query = select(Order).where(Order.id == order_id, Order.user_id == utente.id)
        ordine = db.execute(query).scalar_one_or_none()
    if not ordine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordine non trovato")
    return ordine

@router.put("/orders/{order_id}/status", response_model=OrderRead)
def aggiorna_stato_ordine( order_id: int, dati: OrderStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    ordine = db.get(Order, order_id)
    if not ordine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordine non trovato")
    try:
        nuovo_stato = OrderStatus(dati.stato)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stato non valido")

    try:
        cambia_stato_ordine(nuovo_stato, ordine.stato)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    ordine.stato=nuovo_stato
    db.commit()
    db.refresh(ordine)
    return ordine

@router.post("/orders/{order_id}/rimborso", response_model=OrderRead)
def richiedi_rimborso_ordine(order_id: int, db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    ordine = db.get(Order, order_id)
    if ordine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordine non trovato")
    try:
        richiedi_rimborso(db, ordine, utente)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(ordine)
    return ordine