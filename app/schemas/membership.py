

from __future__ import annotations
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import MembershipRole, MembershipStatus, ProbationStatus


class MembershipBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    company_id: UUID
    role: MembershipRole
    status: MembershipStatus
    manager_membership_id: UUID | None = None
    employment_type: str | None = None
    probation_start_at: date | None = None
    probation_end_at: date | None = None
    probation_status: ProbationStatus | None = None
    onboarding_completed_at: datetime | None = None


class MembershipCreate(MembershipBase):
    """Request model for inviting or creating a membership."""
    pass


class MembershipUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: MembershipRole | None = None
    status: MembershipStatus | None = None
    manager_membership_id: UUID | None = None
    employment_type: str | None = None
    probation_start_at: date | None = None
    probation_end_at: date | None = None
    probation_status: ProbationStatus | None = None
    onboarding_completed_at: datetime | None = None


class MembershipRead(MembershipBase):
    id: UUID
    created_at: datetime
    updated_at: datetime