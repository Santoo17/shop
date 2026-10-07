import pytest
from hypothesis import given, strategies as st
from app.services.order_state import applica_rimborso


@pytest.mark.parametrize(
    "saldo_iniziale, totale_ordine",
    [
        (100.0, -1.0),
        (100.0, 0.0),
    ],
)
def test_applica_rimborso_con_totale_negativo_o_zero_fallisce(saldo_iniziale, totale_ordine):
    with pytest.raises(ValueError) as excinfo:
        applica_rimborso(saldo_iniziale, totale_ordine)
    assert "Il totale dell'ordine non può essere minore o uguale a zero" in str(excinfo.value)


@pytest.mark.parametrize(
    "saldo_iniziale, totale_ordine",
    [
        (-100.0, 50.0),
        (-1.0, 10.0),
        (-50.0, 25.0),
    ],
)
def test_applica_rimborso_con_saldo_negativo_fallisce(saldo_iniziale, totale_ordine):
    with pytest.raises(ValueError) as excinfo:
        applica_rimborso(saldo_iniziale, totale_ordine)
    assert "Il saldo dell'utente non può essere negativo" in str(excinfo.value)


@given(saldo_iniziale=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False), totale_ordine=st.floats(min_value=0.01, max_value=1000.0, allow_nan=False))
def test_applica_rimborso_restituisce_saldo_aggiornato(saldo_iniziale, totale_ordine):
    saldo_aggiornato = applica_rimborso(saldo_iniziale, totale_ordine)
    assert saldo_aggiornato == saldo_iniziale + totale_ordine