from app.models import User, UserRole, Product, DiscountCode, Order, OrderStatus, product
from app.auth import hash_password
from tests.conftest import db_session, make_product

def test_ordine_creato_con_successo(client, db_session, get_user_token, make_product):
    user = get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()

    response = client.post("/checkout", json={
        "items": [{
            "product_id": product.id,
            "quantita": 2
        }], 
        "codice_sconto": None,
    }, headers={"Authorization": f"Bearer {user}"})

    assert response.status_code == 201
    data = response.json()
    assert data["totale"] == 40.0
    assert data["stato"] == OrderStatus.CONFERMATO

def test_ordine_fallito_per_giacenza_insufficiente(client, db_session, get_user_token, make_product):
    user = get_user_token(saldo=100.0)
    product = make_product(prezzo=20.0, giacenza=1)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{
            "product_id": product.id,
            "quantita": 2
        }], 
        "codice_sconto": None,
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_ordine_fallito_per_saldo_insufficiente(client, db_session, get_user_token, make_product):
    user = get_user_token(saldo=10.0)
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{
            "product_id": product.id,
            "quantita": 1
        }], 
        "codice_sconto": None,
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_ordine_fallito_per_codice_sconto_non_valido(client, db_session, get_user_token, make_product):
    user = get_user_token(saldo=100.0)
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{
            "product_id": product.id,
            "quantita": 1
        }], 
        "codice_sconto": "INVALIDCODE",
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_ordine_fallito_per_prodotto_non_esistente(client, db_session, get_user_token):
    user = get_user_token(saldo=100.0)
    response = client.post("/checkout", json={
        "items": [{
            "product_id": 9999,
            "quantita": 1
        }], 
        "codice_sconto": None,
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_ordine_fallito_per_assenza_autenticazione(client, db_session, make_product):
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{
            "product_id": product.id,
            "quantita": 1
        }], 
        "codice_sconto": None,
    })
    assert response.status_code == 401

def test_admin_visualizza_tutti_gli_ordini(client, admin_token):
    admin = admin_token
    response = client.get("/orders", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 200

def test_utente_visualizza_solo_i_propri_ordini(client, get_user_token):
    user = get_user_token()
    response1 = client.get("/orders", headers={"Authorization": f"Bearer {user}"})
    assert response1.status_code == 200

def test_admin_visualizza_dettaglio_ordine(client, make_order, db_session):

    ordine, user, token = make_order()
    user.ruolo = UserRole.ADMIN
    db_session.add(ordine)
    db_session.commit()
    response = client.get(f"/orders/{ordine.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_utente_visualizza_dettaglio_proprio_ordine(client, make_order, db_session, ):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()
    response = client.get(f"/orders/{ordine.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_utente_non_visualizza_dettaglio_ordine_altri(client, make_order, db_session, get_user_token):
    ordine, user, token = make_order()
    db_session.add(ordine)
    db_session.commit()
    user2= get_user_token()
    response = client.get(f"/orders/{ordine.id}", headers={"Authorization": f"Bearer {user2}"})
    assert response.status_code == 404