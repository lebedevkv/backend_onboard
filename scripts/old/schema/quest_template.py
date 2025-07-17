from pydantic import BaseModel
from typing import List, Optional
from app.schemas.quest_step import QuestStepCreate, QuestStepRead
from datetime import datetime
from typing import Optional
from app.schemas.user import UserRead
from app.schemas.company import CompanyRead


class QuestTemplateBase(BaseModel):
    title: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    deadline: datetime
    company_id: Optional[int] = None


class QuestTemplateCreate(QuestTemplateBase):
    steps: List[QuestStepCreate]
    deadline: datetime
    company_id: Optional[int] = None


class QuestTemplateUpdate(QuestTemplateBase):
    steps: Optional[List[QuestStepCreate]] = None
    deadline: Optional[datetime] = None
    company_id: Optional[int] = None


class QuestTemplateRead(QuestTemplateBase):
    id: int
    created_at: datetime
    deadline: datetime
    author: UserRead
    company: Optional[CompanyRead] = None
    steps: List[QuestStepRead]

    class Config:
        from_attributes = True


# Можно использовать Read в качестве Response
QuestTemplateResponse = QuestTemplateRead