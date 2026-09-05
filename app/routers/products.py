from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models import User, Product, UserRole
from app.schemas import ProductCreate, ProductRead, ProductUpdate
from app.auth import require_admin_user

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductRead])
def lista_prodotti(db: Session = Depends(get_db)):
    query = select(Product)
    prodotti = db.execute(query).scalars().all()
    return prodotti

@router.get("/{product_id}", response_model=ProductRead)
def ottieni_prodotto(product_id: int, db: Session = Depends(get_db)):
    prodotto = db.get(Product, product_id)
    if not prodotto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prodotto non trovato")
    return prodotto

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def crea_prodotto(dati: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    nuovo_prodotto = Product(
        nome=dati.nome,
        descrizione=dati.descrizione,
        prezzo=dati.prezzo,
        giacenza=dati.giacenza
    )
    db.add(nuovo_prodotto)
    db.commit()
    db.refresh(nuovo_prodotto)
    return nuovo_prodotto   

@router.put("/{product_id}", response_model=ProductRead)
def aggiorna_prodotto(
    product_id: int,
    dati: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    prodotto = db.get(Product, product_id)
    if not prodotto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prodotto non trovato")
    
    aggioramenti=dati.model_dump(exclude_unset=True)
    for key, value in aggioramenti.items():
        setattr(prodotto, key, value)
    db.commit()
    db.refresh(prodotto)
    return prodotto

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_prodotto(product_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    prodotto = db.get(Product, product_id)
    if not prodotto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prodotto non trovato")
    
    db.delete(prodotto)
    db.commit()
    return None