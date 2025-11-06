import json
import pytest
from app import app
from database import init_db, init_users_table, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Очистка таблицы przed każdym testem
        conn = get_db_connection()
        conn.execute("DELETE FROM produkty")
        conn.commit()
        conn.close()
        yield client

def register_and_get_token(client, login="testuser", password="password123"):
    r = client.post('/register', json={"login": login, "password": password})
    assert r.status_code in (201, 409)
    r2 = client.post('/login', json={"login": login, "password": password})
    assert r2.status_code == 200
    data = r2.get_json()
    return data['access_token']

def test_post_invalid_payload_returns_400(client):
    token = register_and_get_token(client)
    res = client.post('/produkty', json={"nazwa":"ab","cena":"notanumber","ilosc":-1,"kategoria":"x"},
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    j = res.get_json()
    assert 'fieldErrors' in j

def test_post_duplicate_returns_409(client):
    token = register_and_get_token(client, login="dupuser")
    payload = {"nazwa":"UniqueName","cena":10,"ilosc":1,"kategoria":"cat"}
    r1 = client.post('/produkty', json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 201
    r2 = client.post('/produkty', json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 409

def test_delete_nonexistent_returns_404(client):
    token = register_and_get_token(client, login="deluser")
    r = client.delete('/produkty/9999', headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404

def test_missing_token_returns_401(client):
    res = client.post('/produkty', json={"nazwa":"P","cena":1,"ilosc":1,"kategoria":"c"})
    assert res.status_code == 401
