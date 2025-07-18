from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.models.enums import ProbationTaskStatus


class TaskBase(BaseModel):
    """Base schema for probation tasks."""
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    title: str
    description: str | None = None
    due_at: datetime | None = None
    status: ProbationTaskStatus | None = None


class TaskCreate(TaskBase):
    """Request model for creating a probation task."""
    assigned_to_member: UUID


class TaskUpdate(BaseModel):
    """Request model for updating fields of a probation task."""
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None
    status: ProbationTaskStatus | None = None
    result_text: str | None = None


class TaskRead(TaskBase):
    """Response model for reading a probation task."""
    id: UUID
    created_by_member: UUID
    assigned_to_member: UUID
    completed_at: datetime | None = None
    result_text: str | None = None
    created_at: datetime
    updated_at: datetime