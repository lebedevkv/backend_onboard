from __future__ import annotations
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1 import (
    auth, users, companies, employees,
    quests, tasks, evaluations,
    pulse, development
)

app = FastAPI(title="HR Onboard Platform")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables based on models (development only)
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(employees.router)
app.include_router(quests.router)
app.include_router(tasks.router)
app.include_router(evaluations.router)
app.include_router(pulse.router)
app.include_router(development.router)

@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"message": "✅ HR Onboard backend is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )