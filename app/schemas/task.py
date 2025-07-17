from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    status: Optional[str] = "pending"

class TaskCreate(TaskBase):
    assigned_to_id: int
    assigned_by_id: int

class TaskRead(TaskBase):
    id: int
    assigned_to_id: int
    assigned_by_id: int

    class Config:
        from_attributes = True