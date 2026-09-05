from app.models import OrderStatus

TRANSIZIONI_VALIDE = {
    OrderStatus.CONFERMATO: [OrderStatus.SPEDITO, OrderStatus.ANNULLATO],
    OrderStatus.SPEDITO: [OrderStatus.CONSEGNATO, OrderStatus.ANNULLATO],
    OrderStatus.CONSEGNATO: [],
    OrderStatus.ANNULLATO: [],
}

def cambia_stato_ordine(nuovo_stato: OrderStatus, stato_attuale: OrderStatus):
    if nuovo_stato not in TRANSIZIONI_VALIDE[stato_attuale]:
        raise ValueError(f"Transizione non valida da {stato_attuale} a {nuovo_stato}")
    return None