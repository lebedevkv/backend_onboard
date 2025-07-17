# app/tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    data = {
        "full_name": "Тестовый Пользователь",
        "email": "testuser@example.com",
        "password": "securepass123",
        "role": "employee",
        "is_active": True
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200
    assert response.json()["email"] == data["email"]

def test_login_user():
    login = {
        "email": "testuser@example.com",
        "password": "securepass123"
    }
    response = client.post("/auth/login", json=login)
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_get_user_info():
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"