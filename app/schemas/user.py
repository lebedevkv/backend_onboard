from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import GlobalRole


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    locale: str | None = None
    global_role: GlobalRole = GlobalRole.NONE


class UserCreate(UserBase):
    """Request model for registering a new user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr | None = None
    locale: str | None = None
    global_role: GlobalRole | None = None
    password: str | None = Field(None, min_length=8)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime