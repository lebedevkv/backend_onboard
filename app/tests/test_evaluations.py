from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_evaluation():
    evaluation = {
        "employee_id": 1,
        "evaluator_id": 1,
        "score": 5,
        "comments": "Отличная работа"
    }

    response = client.post("/evaluations", json=evaluation)
    assert response.status_code == 200
    assert response.json()["score"] == 5