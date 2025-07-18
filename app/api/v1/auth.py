from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.services.base import UnitOfWork
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Dependency to provide UnitOfWork using the current DB session
def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency to provide AuthService
def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)

@router.post("/register", response_model=UserRead)
def register(
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
) -> UserRead:
    user = service.register(data)
    return user

@router.post("/login", response_model=Token)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
) -> Token:
    user = service.authenticate(data)
    token = service.login(user)
    return token

@router.get("/me", response_model=UserRead)
def me(
    current_user=Depends(get_current_user)
) -> UserRead:
    # current_user is the authenticated User instance
    return UserRead.model_validate(current_user)