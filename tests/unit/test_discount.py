import pytest
from app.models import DiscountCode
import uuid
from app.services import applica_sconto
from tests.conftest import db_session
from hypothesis import given, strategies as st, settings, HealthCheck


def test_sconto_nullo_restituisce_prezzo_originale(db_session):
    prezzo_originale = 100.0
    prezzo_finale = applica_sconto(db_session, prezzo_originale, None)
    assert prezzo_finale == prezzo_originale

def test_sconto_percentuale_applicato_correttamente(db_session):
    prezzo_originale = 200.0
    codice_sconto: DiscountCode = DiscountCode(codice="TEST10", percentuale=10, attivo=True)
    db_session.add(codice_sconto)
    db_session.commit()
    prezzo_finale = applica_sconto(db_session, prezzo_originale, codice_sconto.codice)
    assert prezzo_finale == 180.0  

def test_codice_sconto_invalido_da_errore(db_session):
    prezzo_originale = 150.0
    with pytest.raises(ValueError) as excinfo:
        applica_sconto(db_session, prezzo_originale, "CODICE_INESISTENTE")
    assert "Codice sconto non valido" in str(excinfo.value)

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=100)
@given(totale=st.floats(min_value=0.01, max_value=10000, allow_nan=False), percentuale=st.integers(min_value=1, max_value=25))
def test_sconto_non_da_totale_negativo(db_session, totale, percentuale):
    codice_univoco: str = f"PBTTEST_{uuid.uuid4().hex[:8]}"
    codice_sconto: DiscountCode = DiscountCode(codice=codice_univoco, percentuale=percentuale, attivo=True)
    db_session.add(codice_sconto)
    db_session.commit()
    prezzo_finale = applica_sconto(db_session, totale, codice_sconto.codice)
    assert prezzo_finale >= 0