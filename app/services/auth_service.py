from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.auth import RegisterRequest
from app.models.user import User
from app.utils.security import hash_password
from app.schemas.auth import LoginRequest
from app.utils.security import verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings

def register_user(db: Session, user_data: RegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, login_data: LoginRequest):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный email или пароль")
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный email или пароль")
    return user

def login_and_get_token(user: User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    return token