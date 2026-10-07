from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Review, Product, OrderItem, Order, OrderStatus, User, UserRole
from app.schemas import ReviewCreate, ReviewUpdate


def calcola_media(valutazioni: list[int]) -> float | None:
    if not valutazioni:
        return None
    return sum(valutazioni) / len(valutazioni)


def verifica_puo_aggiornare(autore_id: int, utente_id: int) -> None:
    if autore_id != utente_id:
        raise ValueError("L'utente non è autorizzato ad aggiornare questa recensione.")


def verifica_puo_eliminare(autore_id: int, utente_id: int, ruolo: UserRole) -> None:
    if autore_id != utente_id and ruolo != UserRole.ADMIN:
        raise ValueError("L'utente non è autorizzato a eliminare questa recensione.")


def ha_acquistato_prodotto(db: Session, utente_id: int, prodotto_id: int) -> bool:
    query = (
        select(OrderItem)
        .join(Order)
        .where(
            Order.user_id == utente_id,
            OrderItem.product_id == prodotto_id,
             Order.stato.in_([OrderStatus.CONSEGNATO, OrderStatus.RIMBORSATO]),
        )
        .limit(1)
    )
    return db.execute(query).first() is not None


def ricalcola_valutazione_media(db: Session, prodotto_id: int) -> None:
    query = select(Review.valutazione).where(Review.product_id == prodotto_id)
    valutazioni = list(db.execute(query).scalars())
    prodotto = db.get(Product, prodotto_id)
    prodotto.valutazione_media = calcola_media(valutazioni)
    db.commit()
    db.refresh(prodotto)


def crea_recensione(
    db: Session, utente_id: int, prodotto_id: int, dati: ReviewCreate
) -> Review:
    if not ha_acquistato_prodotto(db, utente_id, prodotto_id):
        raise ValueError(
            "L'utente non ha acquistato questo prodotto, oppure non è stato consegnato e non può recensirlo."
        )
    query = select(Review).where(
        Review.user_id == utente_id, Review.product_id == prodotto_id
    )
    if db.execute(query).scalar_one_or_none() is not None:
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


def aggiorna_recensione(
    db: Session, recensione: Review, dati: ReviewUpdate, utente: User
) -> Review:
    verifica_puo_aggiornare(recensione.user_id, utente.id)
    for chiave, valore in dati.model_dump(exclude_unset=True).items():
        setattr(recensione, chiave, valore)
    db.commit()
    db.refresh(recensione)

    ricalcola_valutazione_media(db, recensione.product_id)
    db.refresh(recensione)
    return recensione


def elimina_recensione(db: Session, recensione: Review, utente: User) -> None:
    verifica_puo_eliminare(recensione.user_id, utente.id, utente.ruolo)
    prodotto_id = recensione.product_id
    db.delete(recensione)
    db.commit()
    ricalcola_valutazione_media(db, prodotto_id)
