from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(..., min_length=8)
    locale: str | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = Field("bearer")


class TokenPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sub: str
    exp: int