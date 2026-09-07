import pytest
from hypothesis import given, strategies as st
from app.models import OrderStatus
from app.services import cambia_stato_ordine, TRANSIZIONI_VALIDE

def test_transazione_valida_non_solleva_errori():
    risultato = cambia_stato_ordine(OrderStatus.SPEDITO, OrderStatus.CONFERMATO)
    assert risultato is None

def test_transazione_non_valida_solleva_errore():
    with pytest.raises(ValueError) as excinfo:
        cambia_stato_ordine(OrderStatus.CONFERMATO, OrderStatus.SPEDITO)
    assert "Transizione non valida" in str(excinfo.value)

@given(stato_attuale=st.sampled_from(OrderStatus), nuovo_stato=st.sampled_from(OrderStatus))
def test_transizioni_valide(stato_attuale, nuovo_stato):
    transizione_valida = nuovo_stato in TRANSIZIONI_VALIDE[stato_attuale]
    if transizione_valida:
        risultato = cambia_stato_ordine(nuovo_stato, stato_attuale)
        assert risultato is None
    else:
        with pytest.raises(ValueError) as excinfo:
            cambia_stato_ordine(nuovo_stato, stato_attuale)
        assert "Transizione non valida" in str(excinfo.value)