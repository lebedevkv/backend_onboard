from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth_service import AuthService
from app.services.base import UnitOfWork, GenericRepository
from app.models.models import User
from app.models.enums import GlobalRole
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Dependency: UnitOfWork
def get_uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(lambda: db)

# Dependency: AuthService
def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)

# Dependency: GenericRepository for User
def get_user_repo(uow: UnitOfWork = Depends(get_uow)) -> GenericRepository[User]:
    return GenericRepository(uow, User)

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user = Depends(get_current_user)
) -> UserRead:
    return UserRead.model_validate(current_user)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service)
) -> UserRead:
    user = service.register(data)
    return UserRead.model_validate(user)

@router.get("/", response_model=list[UserRead])
def list_users(
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> list[UserRead]:
    # Only super-admin can list all users
    if current_user.global_role != GlobalRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав доступа")
    with uow as u:
        users = u.session.query(User).all()
    return [UserRead.model_validate(uobj) for uobj in users]

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: UUID,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> UserRead:
    if current_user.global_role != GlobalRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав доступа")
    with uow as u:
        user = u.session.get(User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
    return UserRead.model_validate(user)

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> UserRead:
    if current_user.global_role != GlobalRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав доступа")
    with uow as u:
        user = u.session.get(User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(user, field, value)
        u.commit()
    return UserRead.model_validate(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    current_user=Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
) -> None:
    if current_user.global_role != GlobalRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав доступа")
    with uow as u:
        user = u.session.get(User, user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
        u.session.delete(user)
        u.commit()
    return