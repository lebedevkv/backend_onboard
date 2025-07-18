from __future__ import annotations
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.base import GenericRepository, UnitOfWork
from app.models.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """Service for user registration, authentication, and token issuance."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self._repo = GenericRepository[User](uow, User)

    def register(self, data: RegisterRequest) -> User:
        """Register a new user."""
        with self.uow as uow:
            # Check for existing email
            existing = uow.session.query(User).filter(User.email == data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists",
                )
            # Hash password and create user
            hashed = hash_password(data.password)
            user = User(email=data.email, password_hash=hashed, locale=data.locale)
            uow.session.add(user)
            uow.commit()
            return user

    def authenticate(self, data: LoginRequest) -> User:
        """Verify credentials and return the user."""
        with self.uow as uow:
            user = uow.session.query(User).filter(User.email == data.email).first()
            if not user or not verify_password(data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password",
                )
            return user

    def login(self, user: User) -> Token:
        """Generate access token for an authenticated user."""
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_str = create_access_token(data={"sub": str(user.id)}, expires_delta=expires)
        return Token(access_token=token_str)