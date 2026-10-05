import pytest
from app.services import calcola_prezzo_scontato
from hypothesis import given, strategies as st, settings

@pytest.mark.parametrize("totale, percentuale, atteso", [
    (100.0, 10, 90.0),
    (200.0, 25, 150.0),
    (50.0, 0, 50.0),
])
def test_calcola_prezzo_scontato(totale, percentuale, atteso):
    prezzo = calcola_prezzo_scontato(totale, percentuale)
    assert prezzo == atteso

def test_sconto_con_percentuale_non_valida_fallisce():
    totale = 100.0
    percentuale = -1
    with pytest.raises(ValueError) as excinfo:
        calcola_prezzo_scontato(totale, percentuale)
    assert "La percentuale di sconto deve essere compresa tra 0 e 100" in str(excinfo.value)
    percentuale = 101
    with pytest.raises(ValueError) as excinfo:
        calcola_prezzo_scontato(totale, percentuale)
    assert "La percentuale di sconto deve essere compresa tra 0 e 100" in str(excinfo.value)

@settings(max_examples=100)
@given(totale=st.floats(min_value=0.01, max_value=10_000, allow_nan=False), percentuale=st.integers(min_value=0, max_value=100))
def test_prezzo_scontato_resta_tra_zero_e_totale(totale, percentuale):
    prezzo = calcola_prezzo_scontato(totale, percentuale)
    assert 0 <= prezzo <= totale


@settings(max_examples=100)
@given(totale=st.floats(min_value=0.01, max_value=10_000, allow_nan=False), percentuale=st.integers(min_value=0, max_value=100))
def test_sconto_e_prezzo_finale_sommano_al_totale(totale, percentuale):
    prezzo = calcola_prezzo_scontato(totale, percentuale)
    sconto= totale * (percentuale / 100)
    assert (prezzo + sconto) == pytest.approx(totale)