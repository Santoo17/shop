from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Review, Product, OrderItem, Order, OrderStatus, User, UserRole
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate

def ha_acquistato_prodotto(db: Session, utente_id: int, prodotto_id: int) -> bool:
    query = select(OrderItem).join(Order).where(
        Order.user_id == utente_id,
        OrderItem.product_id == prodotto_id,
        Order.stato == OrderStatus.CONSEGNATO
    )
    risultato = db.execute(query).scalar_one_or_none()
    return risultato is not None

def crea_recensione(db: Session, utente_id: int, prodotto_id: int, dati: ReviewCreate) -> Review:
    if not ha_acquistato_prodotto(db, utente_id, prodotto_id):
        raise ValueError("L'utente non ha acquistato questo prodotto e non può recensirlo.")
    query = select(Review).where(Review.user_id == utente_id, Review.product_id == prodotto_id)
    esistente_recensione = db.execute(query).scalar_one_or_none()
    if esistente_recensione is not None:
        raise ValueError("L'utente ha già recensito questo prodotto.")

    recensione = Review(
        commento=dati.commento,
        valutazione=dati.valutazione,
        user_id=utente_id,
        product_id=prodotto_id,
    )
    db.add(recensione)
    db.commit()
    db.refresh(recensione)

    ricalcola_valutazione_media(db, prodotto_id)
    db.refresh(recensione)

    return recensione

def ricalcola_valutazione_media(db: Session, prodotto_id: int):
    query = select(Review).where(Review.product_id == prodotto_id)
    recensioni = db.execute(query).scalars().all()
    if recensioni:
        valutazioni = [recensione.valutazione for recensione in recensioni]
        valutazione_media = sum(valutazioni) / len(valutazioni)
    else:
        valutazione_media = None
    prodotto = db.get(Product, prodotto_id)
    prodotto.valutazione_media = valutazione_media
    db.commit()
    db.refresh(prodotto)


def aggiorna_recensione(db: Session, recensione: Review, dati: ReviewUpdate, utente: User) -> Review:
    if recensione.user_id != utente.id and utente.ruolo != UserRole.ADMIN:
        raise ValueError("L'utente non è autorizzato ad aggiornare questa recensione.")
    aggiornamenti = dati.model_dump(exclude_unset=True)
    for chiave, valore in aggiornamenti.items():
        setattr(recensione, chiave, valore)
    db.commit()
    db.refresh(recensione)
    ricalcola_valutazione_media(db, recensione.product_id)
    db.refresh(recensione)
    return recensione



def elimina_recensione(db: Session, recensione: Review, utente: User) -> None:
    if recensione.user_id != utente.id and utente.ruolo != UserRole.ADMIN:
        raise ValueError("L'utente non è autorizzato a eliminare questa recensione.")
    prodotto_id = recensione.product_id
    db.delete(recensione)
    db.commit()
    ricalcola_valutazione_media(db, prodotto_id)
    return None