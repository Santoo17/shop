import pytest
from app.models import OrderStatus, UserRole
from app.services import checkout, richiedi_rimborso, RigaCarrello


def test_da_confermato_a_annullato(db_session, make_order):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()

    richiedi_rimborso(db_session, ordine, user)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.ANNULLATO

def test_da_spedito_a_annullato(db_session, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.SPEDITO
    db_session.add(ordine)
    db_session.commit()
    richiedi_rimborso(db_session, ordine, user)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.ANNULLATO

def test_da_consegnato_a_rimborsato(db_session, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.add(ordine)
    db_session.commit()
  
    richiedi_rimborso(db_session, ordine, user)
    db_session.refresh(ordine)
    assert ordine.stato == OrderStatus.RIMBORSATO

def test_rimborso_non_autorizzato(db_session, make_user, make_order):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()
    altro_utente = make_user()
    db_session.add(altro_utente)
    db_session.commit()

    with pytest.raises(ValueError) as excinfo:
        richiedi_rimborso(db_session, ordine, altro_utente)
    assert "Il richiedente non è autorizzato" in str(excinfo.value)

def test_rimborso_da_admin(db_session, make_user, make_product):
    utente = make_user(saldo=100.0)
    utente_admin = make_user(ruolo=UserRole.ADMIN)
    prodotto = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, utente_admin, prodotto])
    db_session.commit()

    saldo_iniziale = utente.saldo
    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    db_session.commit()

    richiedi_rimborso(db_session, ordine, utente_admin)
    db_session.refresh(ordine)
    db_session.refresh(utente)    

    assert ordine.stato == OrderStatus.ANNULLATO
    assert utente.saldo == saldo_iniziale

def test_rimborso_non_valido(db_session, make_user, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.ANNULLATO
    db_session.add(ordine)
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        richiedi_rimborso(db_session, ordine, user)
    assert "Non è possibile richiedere un rimborso" in str(excinfo.value)