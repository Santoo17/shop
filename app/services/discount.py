from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import DiscountCode


def calcola_prezzo_scontato(totale: float, percentuale: int | None) -> float:
    if percentuale < 0 or percentuale > 100:
        raise ValueError("La percentuale di sconto deve essere compresa tra 0 e 100")
    return totale * (1 - percentuale / 100)


def applica_sconto(db: Session, totale: float, codice_sconto: str | None):
    if codice_sconto is None:
        return totale
    query = select(DiscountCode).where(DiscountCode.codice == codice_sconto)
    sconto = db.execute(query).scalar_one_or_none()
    if sconto is None or not sconto.attivo:
        raise ValueError("Codice sconto non valido")
    return calcola_prezzo_scontato(totale, sconto.percentuale)
