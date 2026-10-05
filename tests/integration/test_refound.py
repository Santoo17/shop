import pytest
from app.models import OrderStatus, UserRole
from app.services import checkout, richiedi_rimborso, cambia_stato_ordine, RigaCarrello


def test_da_confermato_a_annullato(client, db_session, make_order):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()
    db_session.refresh(ordine)
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["stato"] == OrderStatus.ANNULLATO


def test_da_spedito_a_annullato(client,db_session, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.SPEDITO
    db_session.add(ordine)
    db_session.commit()
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["stato"] == OrderStatus.ANNULLATO

def test_da_consegnato_a_rimborsato(client, db_session, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.add(ordine)
    db_session.commit()
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["stato"] == OrderStatus.RIMBORSATO

def test_rimborso_non_autorizzato(client, db_session, get_user_token, make_order):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()
    altro_utente = get_user_token()
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {altro_utente}"})
    assert response.status_code == 400

def test_rimborso_da_admin(client, db_session, make_user, make_product, admin_token):
    utente = make_user(saldo=100.0)
    utente_admin = admin_token
    prodotto = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    saldo_iniziale = utente.saldo
    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    db_session.commit()

    db_session.refresh(ordine)
    db_session.refresh(utente)    
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {utente_admin}"})
    assert response.status_code == 200
    assert ordine.stato == OrderStatus.ANNULLATO
    assert utente.saldo == saldo_iniziale

def test_rimborso_non_valido(client, db_session, make_order):
    ordine, user, token = make_order()
    ordine.stato = OrderStatus.ANNULLATO
    db_session.add(ordine)
    db_session.commit()
    response = client.post(f"/orders/{ordine.id}/rimborso", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400