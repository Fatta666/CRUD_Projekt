import json
import pytest
from app import app
from database import init_db, init_users_table, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
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

import requests
from unittest.mock import Mock
from app import app
from joke_service import JokeClient, ServiceUnavailableError, BadGatewayError 

JOKE_MOCK_SUCCESS = {
    "icon_url": "...", 
    "id": "abc123xyz", 
    "url": "https://...", 
    "value": "Chuck Norris potrafi dzielić przez zero i dostać pieniądze.",
    "created_at": "...",
    "updated_at": "..."
}


def mock_response(status_code, json_data=None):
    """Pomocnicza funkcja do tworzenia odpowiedzi Mock."""
    mock_resp = Mock()
    mock_resp.status_code = status_code
    if json_data is not None:
        mock_resp.json.return_value = json_data
    return mock_resp

def test_joke_happy_path(client, mocker):
    """Test integracyjny 'happy path' - poprawne dane, sensowny JSON."""
    mock_get = mocker.patch('joke_service.requests.get', return_value=mock_response(200, JOKE_MOCK_SUCCESS))

    res = client.get('/external/joke')
    assert res.status_code == 200
    data = res.get_json()
    
    mock_get.assert_called_once()
    
    assert 'joke_text' in data
    assert data['joke_text'] == JOKE_MOCK_SUCCESS['value']
    
def test_joke_external_server_error_502(client, mocker):
    """Test błędu: błąd 5xx po stronie zewnętrznego API (502 Bad Gateway)."""

    mock_get = mocker.patch('joke_service.requests.get', return_value=mock_response(500, {}))

    res = client.get('/external/joke')
    
    assert res.status_code == 502
    data = res.get_json()
    assert data['status'] == 502
    
def test_joke_timeout_503(client, mocker):
    """Test błędu: brak odpowiedzi / timeout (503 Service Unavailable)."""
    mock_get = mocker.patch('joke_service.requests.get', side_effect=requests.exceptions.Timeout)

    res = client.get('/external/joke')
    
    assert res.status_code == 503