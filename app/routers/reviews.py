from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models import User, UserRole, Review
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate
from app.auth import get_current_user, require_admin_user
from app.services import crea_recensione, aggiorna_recensione, elimina_recensione

router = APIRouter(tags=["reviews"])

@router.post("/products/{product_id}/recensioni", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def crea_recensione_prodotto( dati: ReviewCreate, product_id: int, db: Session = Depends(get_db),
                            utente: User = Depends(get_current_user),                            
):
    try:
        recensione = crea_recensione(db, utente.id, product_id, dati)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return recensione

@router.get("/products/{product_id}/recensioni", response_model=list[ReviewRead])
def lista_recensioni(
    product_id: int,
    db: Session = Depends(get_db)
):
    query = select(Review).where(Review.product_id == product_id)
    recensioni = db.execute(query).scalars().all()
    return recensioni

@router.put("/recensioni/{review_id}", response_model=ReviewRead)
def aggiorna_recensione_prodotto(dati: ReviewUpdate, review_id: int, db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    recensione = db.get(Review, review_id)
    if not recensione:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recensione non trovata")
    try:
        recensione_aggiornata = aggiorna_recensione(db, recensione, dati, utente)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return recensione_aggiornata    

@router.delete("/recensioni/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_recensione_prodotto(review_id: int, db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    recensione = db.get(Review, review_id)
    if not recensione:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recensione non trovata")
    try:
        elimina_recensione(db, recensione, utente)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    