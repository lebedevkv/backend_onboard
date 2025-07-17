# app/schemas/quest_step.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserRead


class QuestStepBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    points: int
    deadline: datetime


class QuestStepCreate(QuestStepBase):
    title: str
    author_id: int


class QuestStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    points: Optional[int] = None
    deadline: Optional[datetime] = None
    author_id: Optional[int] = None


class QuestStepRead(QuestStepBase):
    id: int
    quest_template_id: int
    points: int
    deadline: datetime
    author: UserRead

    class Config:
        from_attributes = True


class QuestStepResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order: int
    quest_template_id: int
    points: int
    deadline: datetime
    author: UserRead

    class Config:
        from_attributes = True