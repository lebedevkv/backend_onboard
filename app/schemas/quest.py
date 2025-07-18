from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.models.enums import (
    QuestStatus,
    QuestStepApprovalRole,
    QuestAssignmentStatus,
    StepSubmissionStatus,
)

# Quest schemas
class QuestBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    title: str
    description: str | None = None
    duration_days: int | None = None
    is_mandatory: bool = True
    status: QuestStatus | None = None

class QuestCreate(QuestBase):
    """Request model for creating a new quest template."""
    pass

class QuestUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    description: str | None = None
    duration_days: int | None = None
    is_mandatory: bool | None = None
    status: QuestStatus | None = None

class QuestRead(QuestBase):
    id: UUID
    created_by_member: UUID | None = None
    created_at: datetime
    updated_at: datetime

# Quest Step schemas
class QuestStepBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quest_id: UUID
    title: str
    step_type: str
    required: bool = True
    content_json: dict | None = None
    approval_required_role: QuestStepApprovalRole = QuestStepApprovalRole.NONE
    sort_order: int

class QuestStepCreate(QuestStepBase):
    """Request model for creating a quest step."""
    pass

class QuestStepUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    step_type: str | None = None
    required: bool | None = None
    content_json: dict | None = None
    approval_required_role: QuestStepApprovalRole | None = None
    sort_order: int | None = None

class QuestStepRead(QuestStepBase):
    id: UUID
    created_at: datetime

# Quest Assignment schemas
class QuestAssignmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quest_id: UUID
    membership_id: UUID

class QuestAssignmentCreate(QuestAssignmentBase):
    """Request model for assigning a quest to a member."""
    override_duration_days: int | None = None

class QuestAssignmentRead(QuestAssignmentBase):
    id: UUID
    assigned_by_member: UUID | None = None
    assigned_at: datetime
    due_at: datetime | None = None
    completed_at: datetime | None = None
    status: QuestAssignmentStatus
    progress_percent: float

# Quest Step Submission schemas
class QuestStepSubmissionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quest_assignment_id: UUID
    quest_step_id: UUID
    data_json: dict | None = None

class QuestStepSubmissionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: StepSubmissionStatus
    data_json: dict | None = None

class QuestStepSubmissionRead(QuestStepSubmissionBase):
    id: UUID
    status: StepSubmissionStatus
    submitted_at: datetime | None = None
    reviewed_by_member: UUID | None = None
    reviewed_at: datetime | None = None