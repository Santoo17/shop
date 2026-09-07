def test_client_fixture_funzionality(client):
    response = client.get("/products")
    assert response.status_code == 200