from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.user import UserRead
from app.schemas.company import CompanyRead

# Quest Template Schemas
class QuestTemplateBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline_days: Optional[int] = None
    created_at: Optional[datetime] = None
    company_id: Optional[int] = None

class QuestTemplateCreate(QuestTemplateBase):
    steps: List['QuestStepCreate']
    deadline_days: int
    company_id: Optional[int] = None
    author_id: int

class QuestTemplateUpdate(QuestTemplateBase):
    steps: Optional[List['QuestStepCreate']] = None
    deadline_days: Optional[int] = None
    company_id: Optional[int] = None

class QuestTemplateRead(QuestTemplateBase):
    id: int
    author: Optional[UserRead] = None
    company: Optional[CompanyRead] = None
    steps: List['QuestStepRead']

    class Config:
        from_attributes = True

QuestTemplateResponse = QuestTemplateRead

# Quest Step Schemas
class QuestStepBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0
    points: Optional[int] = 0
    deadline_days: Optional[int] = None

class QuestStepCreate(QuestStepBase):
    author_id: int

class QuestStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    points: Optional[int] = None
    deadline_days: Optional[int] = None
    author_id: Optional[int] = None

class QuestStepRead(QuestStepBase):
    id: int
    quest_template_id: int
    author: Optional[UserRead] = None

    class Config:
        from_attributes = True

class QuestStepResponse(QuestStepRead):
    pass

# Quest Assignment Schemas
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

class QuestAssignmentResponse(BaseModel):
    id: int
    employee_id: int
    template_id: int
    completed: bool
    progress: Optional[List['QuestProgressRead']] = Field(default_factory=list)

    class Config:
        from_attributes = True

# Quest Progress Schemas
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

class QuestProgressRead(QuestProgressBase):
    id: int

    class Config:
        from_attributes = True

class QuestProgressResponse(QuestProgressRead):
    pass

# For forward references
QuestTemplateCreate.update_forward_refs()
QuestTemplateRead.update_forward_refs()
QuestAssignmentResponse.update_forward_refs()