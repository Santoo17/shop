import pytest
from hypothesis import given, strategies as st
from app.models import OrderStatus, UserRole
from app.services import cambia_stato_ordine, TRANSIZIONI_VALIDE, richiedi_rimborso

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



def test_da_confermato_a_annullato(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.CONFERMATO)
    db_session.add(ordine)
    db_session.commit()
    richiedi_rimborso(db_session, ordine, utente)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.ANNULLATO

def test_da_spedito_a_annullato(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.SPEDITO)
    db_session.add(ordine)
    db_session.commit()
    richiedi_rimborso(db_session, ordine, utente)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.ANNULLATO

def test_da_consegnato_a_rimborsato(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.CONSEGNATO)
    db_session.add(ordine)
    db_session.commit()
    richiedi_rimborso(db_session, ordine, utente)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.RIMBORSATO

def test_rimborso_non_autorizzato(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    altro_utente = make_user()
    db_session.add(altro_utente)
    db_session.commit()
    ordine = make_order(user_id=altro_utente.id, stato=OrderStatus.CONFERMATO)
    db_session.add(ordine)
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        richiedi_rimborso(db_session, ordine, utente)
    assert "Il richiedente non è autorizzato" in str(excinfo.value)

def test_da_confermato_a_consegnato_non_valido(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.CONFERMATO)
    db_session.add(ordine)
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        cambia_stato_ordine(OrderStatus.CONSEGNATO, ordine.stato)
    assert "Transizione non valida" in str(excinfo.value)

def test_rimborso_da_admin(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    saldo_iniziale = utente.saldo
    utente_admin = make_user(ruolo=UserRole.ADMIN)
    db_session.add(utente_admin)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.CONFERMATO)
    db_session.add(ordine)
    db_session.commit()
    utente.saldo -=ordine.totale
    richiedi_rimborso(db_session, ordine, utente_admin)
    db_session.refresh(ordine)
    db_session.refresh(utente)
    assert ordine.stato == OrderStatus.ANNULLATO
    assert utente.saldo == saldo_iniziale

def test_rimborso_non_valido(db_session, make_user, make_order):
    utente = make_user()
    db_session.add(utente)
    db_session.commit()
    ordine = make_order(user_id=utente.id, stato=OrderStatus.ANNULLATO)
    db_session.add(ordine)
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        richiedi_rimborso(db_session, ordine, utente)
    assert "Non è possibile richiedere un rimborso" in str(excinfo.value)