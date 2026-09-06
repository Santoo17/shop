from app.models import OrderStatus, User, Order, UserRole
from sqlalchemy.orm import Session

TRANSIZIONI_VALIDE = {
    OrderStatus.CONFERMATO: [OrderStatus.SPEDITO, OrderStatus.ANNULLATO],
    OrderStatus.SPEDITO: [OrderStatus.CONSEGNATO, OrderStatus.ANNULLATO],
    OrderStatus.CONSEGNATO: [OrderStatus.RIMBORSATO],
    OrderStatus.ANNULLATO: [],
    OrderStatus.RIMBORSATO: [],
}

def cambia_stato_ordine(nuovo_stato: OrderStatus, stato_attuale: OrderStatus):
    if nuovo_stato not in TRANSIZIONI_VALIDE[stato_attuale]:
        raise ValueError(f"Transizione non valida da {stato_attuale} a {nuovo_stato}")
    return None

def richiedi_rimborso(db: Session, ordine: Order, richiedente: User):
    if ordine.user_id != richiedente.id and richiedente.ruolo != UserRole.ADMIN:
        raise ValueError("Il richiedente non è autorizzato a richiedere un rimborso per un ordine non suo.")
    if ordine.stato in (OrderStatus.CONFERMATO, OrderStatus.SPEDITO):
        nuovo_stato = OrderStatus.ANNULLATO
    elif ordine.stato == OrderStatus.CONSEGNATO:
        nuovo_stato = OrderStatus.RIMBORSATO
    else:
        raise ValueError(f"Non è possibile richiedere un rimborso per un ordine con stato {ordine.stato}.")

    try:
        cambia_stato_ordine(nuovo_stato, ordine.stato)
    except ValueError as e:
        raise ValueError(f"Transizione non valida: {str(e)}")
    utente_da_rimborsare: User = db.get(User, ordine.user_id)
    utente_da_rimborsare.saldo += ordine.totale
    ordine.stato = nuovo_stato  
    db.commit()
