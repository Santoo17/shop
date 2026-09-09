
from app.models import OrderStatus, Order
def test_utente_fa_recensione_per_prodotto_acquistato_e_consegnato(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user}"})

    ordine_id = response.json()["id"]
    ordine = db_session.get(Order, ordine_id)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 201

from app.models import OrderStatus, Order
def test_utente_fa_recensione_per_prodotto_acquistato_e_non_consegnato(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user}"})


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_utente_fa_recensione_per_prodotto_non_acquistato(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 400

def test_utente_chiede_lista_recensioni_per_prodotto(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.get(f"/products/{product.id}/recensioni", headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 200

def test_utente_modifica_recensione_sua(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user}"})
    ordine_id = response.json()["id"]
    ordine = db_session.get(Order, ordine_id)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user}"})
    

    assert product.valutazione_media == 4.0
    review_id = response.json()["id"]
    response = client.put(f"/recensioni/{review_id}", json={
        "commento": "Recensione modificata",
        "valutazione": 5
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 200
    assert product.valutazione_media == 5.0

def test_utente_modifica_recensione_altrui_fallisce(client, db_session, get_user_token, make_product):
    user1=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user1}"})
    ordine_id = response.json()["id"]
    ordine = db_session.get(Order, ordine_id)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user1}"})
    
    review_id = response.json()["id"]
    user2=get_user_token()

    response = client.put(f"/recensioni/{review_id}", json={
        "commento": "Recensione modificata",
        "valutazione": 5
    }, headers={"Authorization": f"Bearer {user2}"})
    assert response.status_code == 403

def test_utente_elimina_recensione_sua(client, db_session, get_user_token, make_product):
    user=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user}"})
    ordine_id = response.json()["id"]
    ordine = db_session.get(Order, ordine_id)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user}"})
    
    review_id = response.json()["id"]
    response = client.delete(f"/recensioni/{review_id}", headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 204


def test_utente_elimina_recensione_altrui_fallisce(client, db_session, get_user_token, make_product):
    user1=get_user_token()
    product = make_product(prezzo=20.0, giacenza=10)
    db_session.add(product)
    db_session.commit()
    response = client.post("/checkout", json={
        "items": [{ "product_id": product.id, "quantita": 3 }],
        "codice_sconto": None
    }, headers={"Authorization": f"Bearer {user1}"})
    ordine_id = response.json()["id"]
    ordine = db_session.get(Order, ordine_id)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()


    response = client.post(f"/products/{product.id}/recensioni", json={
        "commento": "Recensione di test",
        "valutazione": 4
    }, headers={"Authorization": f"Bearer {user1}"})
    
    review_id = response.json()["id"]
    user2=get_user_token()
    response = client.delete(f"/recensioni/{review_id}", headers={"Authorization": f"Bearer {user2}"})
    assert response.status_code == 403