from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import DiscountCode


def applica_sconto(db: Session, totale: float, codice_sconto: str | None):
    if codice_sconto is None:
        return totale
    query= select(DiscountCode).where(DiscountCode.codice == codice_sconto)
    sconto = db.execute(query).scalar_one_or_none()
    if sconto is None or not sconto.attivo:
        raise ValueError("Codice sconto non valido")
    return totale * (1 - sconto.percentuale / 100)