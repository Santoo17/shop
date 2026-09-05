from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core import get_db
from app.models import User
from app.schemas import UserRead, UserUpdate, AdminUpdate
from app.auth import get_current_user, require_admin_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
def get_me(utente: User = Depends(get_current_user)):
    return utente

@router.put("/me", response_model=UserRead)
def update_me(dati: UserUpdate, db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    aggioramenti = dati.model_dump(exclude_unset=True)
    for key, value in aggioramenti.items():
        setattr(utente, key, value)
    db.commit()
    db.refresh(utente)
    return utente

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), utente: User = Depends(get_current_user)):
    db.delete(utente)
    db.commit()
    return None

@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    query = select(User)
    utenti = db.execute(query).scalars().all()
    return utenti

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, dati: AdminUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    utente = db.get(User, user_id)
    if not utente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    aggioramenti = dati.model_dump(exclude_unset=True)
    for key, value in aggioramenti.items():
        setattr(utente, key, value)
    db.commit()
    db.refresh(utente)
    return utente

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    utente = db.get(User, user_id)
    if not utente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")
    db.delete(utente)
    db.commit()
    return None