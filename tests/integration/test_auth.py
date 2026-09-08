def test_registrazione_e_login_utente(client):
    client.post("/auth/register", json={
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@test.com",
        "password": "password123",
    })

    response = client.post("/auth/login", data={
        "username": "mario@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_fallito(client):
    client.post("/auth/register", json={
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@test.com",
        "password": "password123",
    })
    response = client.post("/auth/login", data={
        "username": "mario@test.com",
        "password": "password_sbagliata"
    })
    assert response.status_code == 401


def test_registrazione_fallita_email_duplicata(client):
    client.post("/auth/register", json={
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@test.com",
        "password": "password123",
    })
    response = client.post("/auth/register", json={
        "nome": "Luigi",
        "cognome": "Verdi", 
        "email": "mario@test.com",
        "password": "password123",
    })
    assert response.status_code == 400

def test_accesso_senza_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_accesso_con_token(client):
    client.post("/auth/register", json={
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@test.com",
        "password": "password123",
    })

    response = client.post("/auth/login", data={
        "username": "mario@test.com",
        "password": "password123",
    })

    token = response.json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "mario@test.com"

def test_utente_non_autorizzato(client):
    client.post("/auth/register", json={
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario@test.com",
        "password": "password123",
    })
    response = client.post("/auth/login", data={
        "username": "mario@test.com",
        "password": "password123",
    })
    token = response.json()["access_token"]
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_accesso_con_token_invalido(client):
    response = client.get("/users/me", headers={"Authorization": "token_invalido"})
    assert response.status_code == 401