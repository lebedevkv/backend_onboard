from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    # Создание тестового задания
    task_data = {
        "title": "Подготовить отчет",
        "description": "Сформировать отчет по продажам",
        "assigned_to_id": 1,
        "assigned_by_id": 1,
        "status": "pending"
    }

    response = client.post("/tasks", json=task_data)
    assert response.status_code in [200, 201]
    task = response.json()
    assert task["title"] == "Подготовить отчет"