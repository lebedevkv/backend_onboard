from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskRead
from app.services.task_service import create_task
from app.utils.dependencies import get_db

router = APIRouter()

@router.post("/tasks", response_model=TaskRead, tags=["tasks"])
def assign_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task)