
from app.models import Product


def test_creazione_prodotto_da_admin(client, admin_token, make_product):
    prodotto: Product = make_product()
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

def test_creazione_prodotto_da_utente_normale(client, get_user_token, make_product):
    user_token = get_user_token()
    prodotto: Product = make_product()
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403

def test_lista_prodotti(client):
    response = client.get("/products/")
    assert response.status_code == 200

def test_creazione_prodotto_con_prezzo_negativo(client, make_product, admin_token):
    prodotto: Product = make_product(prezzo=-10.0)
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 422

def test_creazione_prodotto_con_giacenza_negativa(client, make_product, admin_token):
    prodotto: Product = make_product(giacenza=-10)
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 422

def test_richiesta_prodotto_non_trovato(client):
    response = client.get("/products/9999")
    assert response.status_code == 404

def test_aggiornamento_prodotto_da_admin(client, admin_token, make_product):
    prodotto: Product = make_product()
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {admin_token}"})
    prodotto_id = response.json()["id"]

    response = client.put(f"/products/{prodotto_id}", json={
        "nome": "Prodotto Aggiornato",
        "descrizione": "Descrizione Aggiornata",
        "prezzo": 100.0,
        "giacenza": 20
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["nome"] == "Prodotto Aggiornato"

def test_aggiornamento_prodotto_da_utente_normale(client, get_user_token, admin_token, make_product):
    prodotto: Product = make_product()
    response = client.post("/products/", json={
        "nome": prodotto.nome,
        "descrizione": prodotto.descrizione,
        "prezzo": prodotto.prezzo,
        "giacenza": prodotto.giacenza
    }, headers={"Authorization": f"Bearer {admin_token}"})
    prodotto_id = response.json()["id"]
    response = client.put(f"/products/{prodotto_id}", json={
        "nome": "Prodotto Aggiornato",
        "descrizione": "Descrizione Aggiornata",
        "prezzo": 100.0,
        "giacenza": 20
    }, headers={"Authorization": f"Bearer {get_user_token()}"})

    assert response.status_code == 403