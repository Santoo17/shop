import pytest
from hypothesis import given, strategies as st

from app.models import UserRole
from app.services.review import (
    calcola_media,
    verifica_puo_aggiornare,
    verifica_puo_eliminare,
)

voti = st.lists(st.integers(1, 5), min_size=1, max_size=50)


def test_nessuna_recensione_nessuna_media():
    assert calcola_media([]) is None


@pytest.mark.parametrize(
    "valutazioni, atteso",
    [([4], 4.0), ([4, 2], 3.0), ([1, 2], 1.5), ([5, 4, 4, 5], 4.5)],
)
def test_media_di_esempi_noti(valutazioni, atteso):
    assert calcola_media(valutazioni) == pytest.approx(atteso)

def test_l_autore_puo_aggiornare():
    assert verifica_puo_aggiornare(autore_id=1, utente_id=1) is None


def test_un_altro_utente_non_puo_aggiornare():
    with pytest.raises(ValueError, match="aggiornare") as exc_info:
        verifica_puo_aggiornare(autore_id=1, utente_id=2)
    assert "L'utente non è autorizzato" in str(exc_info.value)


def test_eliminazione_vietata_a_chi_non_e_autore_ne_admin():
    with pytest.raises(ValueError, match="eliminare") as exc_info:
        verifica_puo_eliminare(autore_id=1, utente_id=2, ruolo=UserRole.STANDARD)
    assert "L'utente non è autorizzato" in str(exc_info.value)


def test_admin_puo_eliminare_recensione_di_un_altro_utente():
    assert verifica_puo_eliminare(autore_id=1, utente_id=2, ruolo=UserRole.ADMIN) is None



@given(valutazioni=voti)
def test_la_media_sta_tra_il_voto_minimo_e_massimo(valutazioni):
    minimo=0
    massimo=5    
    assert minimo <= calcola_media(valutazioni) <= massimo