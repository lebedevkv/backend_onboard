from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    register_data = {
        "full_name": "Иван Иванов",
        "email": "ivan@example.com",
        "password": "strongpass123"
    }

    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    assert response.json()["email"] == "ivan@example.com"

    login_data = {
        "email": "ivan@example.com",
        "password": "strongpass123"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "ivan@example.com"