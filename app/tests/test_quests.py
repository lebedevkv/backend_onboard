from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_quest_step():
    quest_step = {
        "title": "Познакомиться с коллегами",
        "description": "Пройтись по отделу и представиться",
        "order": 1,
        "is_required": True,
        "template_name": "onboarding_week_1"
    }

    response = client.post("/quests/steps", json=quest_step)
    assert response.status_code == 200
    assert response.json()["title"] == quest_step["title"]