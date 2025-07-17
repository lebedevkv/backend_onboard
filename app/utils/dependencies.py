from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить токен",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_id(user_id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не содержит ID пользователя")

    user = get_user_by_id(user_id=int(user_id), db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


# --- Ролевые проверки ---



def require_admin_or_hr(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "super_admin":
        return current_user
    if current_user.role == "company_admin" or current_user.role == "hr":
        return current_user
    raise HTTPException(status_code=403, detail="Недостаточно прав доступа")


def require_company_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "super_admin":
        return current_user
    if current_user.role == "company_admin":
        return current_user
    raise HTTPException(status_code=403, detail="Недостаточно прав доступа")


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Доступ разрешён только супер-администратору")
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "super_admin":
        return current_user
    if current_user.role == "company_admin":
        return current_user
    if current_user.role == "manager":
        return current_user
    raise HTTPException(status_code=403, detail="Недостаточно прав доступа")


def require_employee(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Требуется роль сотрудника")
    return current_user

def require_mentor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Требуется роль наставника")
    return current_user


# Универсальная проверка ролей
def require_roles(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == "super_admin":
            return current_user
        if current_user.role in roles:
            return current_user
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа")
    return role_checker