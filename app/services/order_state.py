from app.models import OrderStatus, User, Order, UserRole, Product, OrderItem
from sqlalchemy.orm import Session
from sqlalchemy import select, update

TRANSIZIONI_VALIDE = {
    OrderStatus.CONFERMATO: [OrderStatus.SPEDITO, OrderStatus.ANNULLATO],
    OrderStatus.SPEDITO: [OrderStatus.CONSEGNATO, OrderStatus.ANNULLATO],
    OrderStatus.CONSEGNATO: [OrderStatus.RIMBORSATO],
    OrderStatus.ANNULLATO: [],
    OrderStatus.RIMBORSATO: [],
}


def cambia_stato_ordine(nuovo_stato: OrderStatus, stato_attuale: OrderStatus):
    if nuovo_stato not in TRANSIZIONI_VALIDE[stato_attuale]:
        raise ValueError(f"Transizione non valida da {stato_attuale.value} a {nuovo_stato.value}")
    return nuovo_stato


def richiedi_rimborso(db: Session, ordine: Order, richiedente: User):
    if ordine.user_id != richiedente.id and richiedente.ruolo != UserRole.ADMIN:
        raise ValueError(
            "Il richiedente non è autorizzato a richiedere un rimborso per un ordine non suo."
        )

    if ordine.stato in (OrderStatus.CONFERMATO, OrderStatus.SPEDITO):
        ordine.stato = cambia_stato_ordine(OrderStatus.ANNULLATO, ordine.stato)
    elif ordine.stato == OrderStatus.CONSEGNATO:
        ordine.stato = cambia_stato_ordine(OrderStatus.RIMBORSATO, ordine.stato)
    else:
        raise ValueError(
            f"Non è possibile richiedere un rimborso per un ordine con stato {ordine.stato.value}."
        )

    utente_da_rimborsare: User = db.get(User, ordine.user_id)
    utente_da_rimborsare.saldo = applica_rimborso(utente_da_rimborsare.saldo, ordine.totale)
    ripristina_giacenza(db, ordine)
    db.commit()


def ripristina_giacenza(db: Session, ordine: Order) -> None:
    righe = db.execute(
        select(OrderItem.product_id, OrderItem.quantita).where(
            OrderItem.order_id == ordine.id
        )
    ).all()
    for product_id, quantita in righe:
        db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(giacenza=Product.giacenza + quantita)
        )


def applica_rimborso(saldo: float, totale: float) -> float:
    if totale <= 0:
        raise ValueError("Il totale dell'ordine non può essere minore o uguale a zero")
    if saldo < 0:
        raise ValueError("Il saldo dell'utente non può essere negativo")
    return saldo + totale

