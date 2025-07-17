from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.v1 import auth, users, company, employee, tasks, evaluations, pulse, development, quest

app = FastAPI(title="HR Onboard Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:63342"] — точечно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Только на этапе разработки — создаёт таблицы по моделям
Base.metadata.create_all(bind=engine)

# Подключение маршрутов
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(company.router, prefix="/companies", tags=["companies"])
app.include_router(employee.router, prefix="/employees", tags=["employees"])
app.include_router(quest.router, prefix="/quests", tags=["quests"])


app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
app.include_router(pulse.router, prefix="/pulse", tags=["pulse"])
app.include_router(development.router, prefix="/development", tags=["development"])

@app.get("/")
def root():
    return {"message": "✅ HR Onboard backend работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010, reload=True)