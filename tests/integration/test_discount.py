from urllib import response


def test_leggi_sconti(client):
    response = client.get("/discounts")
    assert response.status_code == 200

def test_admin_crea_sconto(client, admin_token):
    admin = admin_token
    response = client.post("/discounts", json={
        "codice": "TEST10",
        "percentuale": 10.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 201

def test_utente_crea_sconto_fallito(client, get_user_token):
    user = get_user_token()
    response = client.post("/discounts", json={
        "codice": "TEST20",
        "percentuale": 20.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 403

def test_admin_aggiorna_sconto(client, admin_token, db_session):
    admin = admin_token

    response = client.post("/discounts", json={
        "codice": "TEST20",
        "percentuale": 20.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {admin}"})
    sconto_id = response.json()["id"]

    response = client.put(f"/discounts/{sconto_id}", json={
        "codice": "TEST15",
        "percentuale": 15.0,
        "attivo": False
    }, headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["percentuale"] == 15.0
    assert data["attivo"] is False

def test_admin_elimina_sconto(client, admin_token):
    admin = admin_token

    response = client.post("/discounts", json={
        "codice": "TEST20",
        "percentuale": 20.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {admin}"})
    sconto_id = response.json()["id"]

    response = client.delete(f"/discounts/{sconto_id}", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 204

def test_utente_elimina_sconto_fallito(client, get_user_token, admin_token):
    user = get_user_token()
    admin = admin_token
    response = client.post("/discounts", json={
        "codice": "Codice10", 
        "percentuale": 10.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {admin}"})
    sconto_id = response.json()["id"]

    response = client.delete(f"/discounts/{sconto_id}", headers={"Authorization": f"Bearer {user}"})
    assert response.status_code == 403

def test_elimina_sconto_non_trovato(client, admin_token):
    admin = admin_token
    response = client.delete("/discounts/9999", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 404

def test_aggiorna_sconto_non_trovato(client, admin_token):
    admin = admin_token
    response = client.put("/discounts/9999", json={
        "codice": "TEST11",
        "percentuale": 11.0,
        "attivo": True
    }, headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 404