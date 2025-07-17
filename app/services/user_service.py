from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password
from app.db.session import SessionLocal
from app.models import User, Employee

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = hash_password(user_data.password)
    db_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active,
        company=user_data.company,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def update_user(db: Session, user: User, updates: UserUpdate) -> User:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def get_all_users():
    with SessionLocal() as db:
        return db.query(User).all()

def get_users_by_company(company: str):
    if not company:
        return []
    with SessionLocal() as db:
        return db.query(User).filter(User.company == company).all()