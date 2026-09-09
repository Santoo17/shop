def test_utente_visualizza_se_stesso(client, get_user_token):
    user_token = get_user_token()
    response = client.get("/users/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

def test_utente_modica_se_stesso(client, get_user_token):
    user = get_user_token()

    response= client.put("/users/me", headers={"Authorization": f"Bearer {user}"}, json={"nome": "NuovoNome"})
    assert response.status_code == 200
    assert response.json()["nome"] == "NuovoNome"

def test_utente_modifica_altri_fallisce(client, get_user_token):
    response= client.post("/auth/register", json={ "nome": "User1","cognome": "User1Cognome", "email": "user1@example.com", "password": "password123" })
    user_id = response.json()["id"]
    user2= get_user_token()

    response = client.put(f"/users/{user_id}", headers={"Authorization": f"Bearer {user2}"}, json={"nome": "NuovoNome"})
    assert response.status_code == 403
    
def test_utente_admin_modifica_altri_successo(client, db_session, admin_token, make_user):
    user = make_user()
    db_session.add(user)
    db_session.commit()
    user_id = user.id
    admin = admin_token

    response = client.put(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin}" }, json={"nome": "NuovoNome"})
    assert response.status_code == 200

def test_utente_admin_modifica_altri_fallisce_se_non_esiste(client, db_session, admin_token):
    admin = admin_token
    response = client.put(f"/users/9999", headers={"Authorization": f"Bearer {admin}" }, json={"nome": "NuovoNome"})
    assert response.status_code == 404

def test_admin_visualizza_lista_utenti(client, admin_token):
    admin = admin_token
    response = client.get("/users/", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 200

def test_utente_standard_visualizza_lista_utenti_fallisce(client, get_user_token):
    user_token = get_user_token()
    response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403

def test_utente_elimina_se_stesso(client, get_user_token):
    user_token = get_user_token()
    response = client.delete("/users/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 204

def test_utente_elimina_altri_fallisce(client, get_user_token, make_user, db_session):
    user = make_user()
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    user2= get_user_token()

    response = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {user2}"})
    assert response.status_code == 403

def test_utente_admin_elimina_altri_successo(client, db_session, admin_token, make_user):
    user = make_user()
    db_session.add(user)
    db_session.commit()
    user_id = user.id
    admin = admin_token

    response = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 204

def test_utente_admin_elimina_altri_fallisce_se_non_esiste(client, db_session, admin_token):
    admin = admin_token
    response = client.delete(f"/users/9999", headers={"Authorization": f"Bearer {admin}"})
    assert response.status_code == 404