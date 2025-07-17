from pydantic import BaseModel
from typing import Optional

class QuestProgressBase(BaseModel):
    step_id: int
    assignment_id: int
    is_completed: bool
    comment: Optional[str] = None

class QuestProgressCreate(BaseModel):
    step_id: int
    assignment_id: int
    comment: Optional[str] = None
    is_completed: bool = False

class QuestProgressUpdate(BaseModel):
    comment: Optional[str] = None
    is_completed: Optional[bool] = None

class QuestProgressResponse(BaseModel):
    id: int
    step_id: int
    assignment_id: int
    comment: Optional[str]
    is_completed: bool

    class Config:
        from_attributes = True

class QuestProgressRead(QuestProgressBase):
    id: int

    class Config:
        from_attributes = True