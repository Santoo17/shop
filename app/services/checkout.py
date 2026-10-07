from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.services import applica_sconto
from app.models import Product, Order, OrderStatus, OrderItem, User


@dataclass
class RigaCarrello:
    product_id: int
    quantita: int


def aggrega_carrello(carrello: list[RigaCarrello]) -> dict[int, int]:
    quantita_per_prodotto: dict[int, int] = {}
    for riga in carrello:
        if riga.quantita <= 0:
            raise ValueError("La quantità deve essere maggiore di zero")
        quantita_per_prodotto[riga.product_id] = (
            quantita_per_prodotto.get(riga.product_id, 0) + riga.quantita
        )
    if not quantita_per_prodotto:
        raise ValueError("Il carrello è vuoto")
    return quantita_per_prodotto


def checkout(
    db: Session, utente: User, carello: list[RigaCarrello], codice_sconto: str | None
) -> Order:
    quantita_per_prodotto = aggrega_carrello(carello)
    prodotti: list[tuple[Product, int]] = []
    for product_id, quantita in quantita_per_prodotto.items():
        prodotto = db.get(Product, product_id)
        if prodotto is None:
            raise ValueError(f"Prodotto con ID {product_id} non trovato")
        if prodotto.giacenza < quantita:
            raise ValueError(f"Quantità insufficiente per il prodotto {prodotto.nome}")
        prodotti.append((prodotto, quantita))
    totale = sum(prodotto.prezzo * quantita for prodotto, quantita in prodotti)
    totale = applica_sconto(db, totale, codice_sconto)

    if utente.saldo < totale:
        raise ValueError("Saldo insufficiente")

    if totale <= 0:
        raise ValueError("Il totale dell'ordine deve essere maggiore di zero")

    ordine = Order(
        user_id=utente.id,
        totale=totale,
        stato=OrderStatus.CONFERMATO,
        codice_sconto=codice_sconto,
    )

    for prodotto, quantita in prodotti:
        riga_ordine = OrderItem(
            product_id=prodotto.id,
            quantita=quantita,
            prezzo_unitario=prodotto.prezzo,
        )
        prodotto.giacenza -= quantita
        ordine.items.append(riga_ordine)

    utente.saldo -= totale

    db.add(ordine)
    db.commit()
    db.refresh(ordine)

    return ordine
