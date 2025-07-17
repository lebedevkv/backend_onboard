from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.schemas.quest_step import QuestStepRead
from pydantic import Field

class QuestAssignmentBase(BaseModel):
    employee_id: int
    template_id: int

class QuestAssignmentCreate(QuestAssignmentBase):
    deadline: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestAssignmentRead(QuestAssignmentBase):
    id: int
    deadline: Optional[datetime] = None
    status: str
    steps: List[QuestStepRead]

    class Config:
        from_attributes = True

class QuestAssignmentResponse(QuestAssignmentBase):
    id: int
    completed: bool
    progress: Optional[List[QuestStepRead]] = Field(default_factory=list)

    class Config:
        from_attributes = True