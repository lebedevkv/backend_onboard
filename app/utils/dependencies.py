from __future__ import annotations
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.utils.security import get_current_user          # JWT-валидация + User
from app.models.models import Membership
from app.models.enums import GlobalRole, MembershipRole, MembershipStatus

# ---------------------------------------------------------------------------
# DB-сессия
# ---------------------------------------------------------------------------

def get_db() -> Callable[[], Session]:
    """Yield SQLAlchemy session for request scope."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Глобальные проверки ролей
# ---------------------------------------------------------------------------

def require_super_admin(current_user=Depends(get_current_user)):
    if current_user.global_role != GlobalRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль SuperAdmin",
        )
    return current_user


def require_global_roles(*roles: GlobalRole):
    """Factory-dependency: пропускает, если global_role пользователя
    входит в список *roles либо он SuperAdmin."""
    def checker(current_user=Depends(get_current_user)):
        if current_user.global_role == GlobalRole.SUPER_ADMIN:
            return current_user
        if current_user.global_role in roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа",
        )
    return checker

# ---------------------------------------------------------------------------
# Membership helpers
# ---------------------------------------------------------------------------

def get_active_membership(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Membership | None:
    """Возвращает первое ACTIVE-членство текущего пользователя."""
    return (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.status == MembershipStatus.ACTIVE,
        )
        .first()
    )


def require_membership_roles(*roles: MembershipRole):
    """Factory-dependency: проверяет роль активного Membership."""
    def checker(membership=Depends(get_active_membership)):
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет активного членства",
            )
        if membership.role == MembershipRole.OWNER or membership.role in roles:
            return membership
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа",
        )
    return checker