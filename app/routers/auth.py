from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models import User, UserRole
from app.schemas import UserRead, UserCreate, UserLogin, Token
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(dati: UserCreate, db: Session = Depends(get_db)):
    query= select(User).where(User.email == dati.email)
    esistente = db.execute(query).scalar_one_or_none()
    if esistente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Utente già registrato")
    nuovo_utente = User(
        nome=dati.nome,
        cognome=dati.cognome,
        email=dati.email,
        password_digest=hash_password(dati.password),
        indirizzo=dati.indirizzo,
        ruolo=UserRole.STANDARD,
        saldo=0.0
    )
    db.add(nuovo_utente)
    db.commit()
    db.refresh(nuovo_utente)
    return nuovo_utente

@router.post("/login", response_model= Token)
def login(dati: UserLogin, db: Session = Depends(get_db)):
    query= select(User).where(User.email == dati.email)
    utente = db.execute(query).scalar_one_or_none()
    if not utente or not verify_password(dati.password , utente.password_digest):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenziali non valide")
    access_token = create_access_token({"sub": str(utente.id)})
    return {"access_token": access_token, "token_type": "bearer"}