from dataclasses import dataclass
from sqlalchemy.orm import Session  
from app.services import applica_sconto
from app.models import Product, Order, OrderStatus, OrderItem, User

@dataclass
class RigaCarrello:
    product_id: int
    quantita: int

def checkout(db: Session, utente: User, carello: list[RigaCarrello], codice_sconto: str | None) -> Order:
    prodotti: list[tuple[Product, int]] = [ ]
    for riga in carello:
        prodotto= db.get(Product, riga.product_id)
        if prodotto is None:
            raise ValueError(f"Prodotto con ID {riga.product_id} non trovato")
        if prodotto.giacenza < riga.quantita:
            raise ValueError(f"Quantità insufficiente per il prodotto {prodotto.nome}")
        prodotti.append((prodotto, riga.quantita))
    totale = sum(prodotto.prezzo *quantita for prodotto, quantita in prodotti)
    totale = applica_sconto(db, totale, codice_sconto)

    if utente.saldo < totale:
        raise ValueError("Saldo insufficiente")

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
    