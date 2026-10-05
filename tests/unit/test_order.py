import pytest
from hypothesis import given, strategies as st

from app.services import RigaCarrello, aggrega_carrello

def test_righe_dello_stesso_prodotto_vengono_aggregate():
    carrello = [ RigaCarrello(product_id=1, quantita=2), RigaCarrello(product_id=2, quantita=1), RigaCarrello(product_id=1, quantita=3) ]
    risultato = aggrega_carrello(carrello)
    assert risultato == { 1: 5, 2: 1 }

def test_quantita_negativa_fallisce():
    carrello = [ RigaCarrello(product_id=1, quantita=-1) ]
    with pytest.raises(ValueError) as excinfo:
        aggrega_carrello(carrello)
    assert "La quantità deve essere maggiore di zero" in str(excinfo.value)

def test_carrello_vuoto_fallisce():
    carrello = []
    with pytest.raises(ValueError) as excinfo:
        aggrega_carrello(carrello)
    assert "Il carrello è vuoto" in str(excinfo.value)


@given(id_prodotto=st.integers(1, 5), quantita=st.integers(1, 5), errore=st.integers(-5, 0))
def test_riga_non_positiva_fa_fallire_intero_carrello(id_prodotto, quantita, errore):
    carrello = [ RigaCarrello(product_id=id_prodotto, quantita=quantita), RigaCarrello(product_id=id_prodotto, quantita=errore) ]
    with pytest.raises(ValueError) as excinfo:
        aggrega_carrello(carrello)
    assert "La quantità deve essere maggiore di zero" in str(excinfo.value)