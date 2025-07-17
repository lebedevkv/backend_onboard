import os

BASE_DIR = "/Users/lebedevkv/PycharmProjects/backend_onboard"

structure = {
    "app": {
        "main.py": "",
        "core": {"config.py": ""},
        "db": {"base.py": "", "base_class.py": "", "session.py": ""},
        "models": {
            "user.py": "", "employee.py": "", "quest.py": "", "task.py": "",
            "evaluation.py": "", "pulse.py": "", "development_plan.py": ""
        },
        "schemas": {
            "user.py": "", "auth.py": "", "quest.py": "", "task.py": "",
            "evaluation.py": "", "pulse.py": "", "development_plan.py": ""
        },
        "api": {
            "v1": {
                "auth.py": "", "users.py": "", "quests.py": "", "tasks.py": "",
                "evaluations.py": "", "pulse.py": "", "development.py": ""
            }
        },
        "services": {
            "auth_service.py": "", "user_service.py": "", "quest_service.py": "",
            "task_service.py": "", "evaluation_service.py": ""
        },
        "utils": {"security.py": "", "dependencies.py": ""},
        "templates": {},
        "tests": {
            "test_auth.py": "", "test_quests.py": "",
            "test_tasks.py": "", "test_evaluations.py": ""
        }
    },
    "alembic/versions/.keep": "",
    ".env": "",
    "requirements.txt": "",
    "Dockerfile": "",
    "docker-compose.yml": "",
    "alembic.ini": "",
    "README.md": ""
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        full_path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(full_path, exist_ok=True)
            create_structure(full_path, content)
        else:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

create_structure(BASE_DIR, structure)
print(f"✅ Проект создан по пути: {BASE_DIR}")