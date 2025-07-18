

from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import PlanTier, SignupMode, CompanyStatus


class CompanyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str | None = None
    timezone: str | None = None
    plan_tier: PlanTier | None = None
    signup_mode: SignupMode | None = None
    status: CompanyStatus | None = None
    default_quest_duration_days: int | None = None
    blocked_until_onboarding_complete: bool | None = None


class CompanyCreate(CompanyBase):
    """Request model for creating a new company via self-signup or admin."""
    pass


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    slug: str | None = None
    timezone: str | None = None
    plan_tier: PlanTier | None = None
    signup_mode: SignupMode | None = None
    status: CompanyStatus | None = None
    default_quest_duration_days: int | None = None
    blocked_until_onboarding_complete: bool | None = None


class CompanyRead(CompanyBase):
    id: UUID
    default_quest_id: UUID | None = None
    created_by_user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime