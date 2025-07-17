from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate

def create_task(db: Session, task_data: TaskCreate) -> Task:
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def mark_task_completed(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "done"
        db.commit()
        db.refresh(task)
    return task