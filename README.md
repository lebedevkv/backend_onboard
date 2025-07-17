# HR Platform (Backend)

## Компоненты

- FastAPI + SQLAlchemy + Pydantic
- PostgreSQL via Docker
- Alembic для миграций
- JWT авторизация
- Пульс-опросы, квесты, задачи, оценки

## Запуск проекта

```bash
docker compose up --build

ENV=local PYTHONPATH=. uvicorn app.main:app --reload --port 8010