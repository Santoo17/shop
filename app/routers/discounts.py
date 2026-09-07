from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core import get_db
from app.models import DiscountCode, User
from app.schemas import DiscountCodeRead, DiscountCodeCreate, DiscountCodeUpdate
from app.auth import get_current_user, require_admin_user

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.get("/", response_model=list[DiscountCodeRead])
def lista_sconti(db: Session = Depends(get_db),):
    query = select(DiscountCode)
    codici_sconto = db.execute(query).scalars().all()
    return codici_sconto

@router.post("/", response_model=DiscountCodeRead, status_code=status.HTTP_201_CREATED)
def crea_sconto(dati: DiscountCodeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    nuovo_sconto = DiscountCode(
        codice=dati.codice,
        percentuale=dati.percentuale,
        attivo=dati.attivo
    )
    db.add(nuovo_sconto)
    db.commit()
    db.refresh(nuovo_sconto)
    return nuovo_sconto

@router.put("/{discount_id}", response_model=DiscountCodeRead)
def aggiorna_sconto(
    discount_id: int,
    dati: DiscountCodeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    sconto = db.get(DiscountCode, discount_id)
    if not sconto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sconto non trovato")
    
    aggioramenti=dati.model_dump(exclude_unset=True)
    for key, value in aggioramenti.items():
        setattr(sconto, key, value)
    db.commit()
    db.refresh(sconto)
    return sconto

@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_sconto(discount_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    sconto = db.get(DiscountCode, discount_id)
    if not sconto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sconto non trovato")
    
    db.delete(sconto)
    db.commit()
    return None