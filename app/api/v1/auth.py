from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserCreate, UserRead
from app.models.employee import Employee
from app.models.company import Company
from app.schemas.user import UserRead
from app.services.user_service import create_user
from app.utils.dependencies import get_db, get_current_user
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, Token
from app.services.auth_service import authenticate_user, login_and_get_token
from app.utils.dependencies import get_db
router = APIRouter()

@router.post("/register", response_model=UserRead, tags=["auth"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    return create_user(db, user)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data)
    token = login_and_get_token(user)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead, tags=["auth"])


def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_data = UserRead.from_orm(current_user)

    employee = db.query(Employee).filter_by(user_id=current_user.id).first()
    if employee:
        user_data.employee_id = employee.id
        user_data.department = employee.department
        user_data.position = employee.position

        company = db.query(Company).filter_by(id=employee.company_id).first()
        if company:
            user_data.company_name = company.name

    return user_data