from typing import List, Literal
from fastapi import Query

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.services.user_service import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    get_all_users,
    get_users_by_company,
)
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.schemas.user import RoleUpdate
from app.models.user import User
from app.models.employee import Employee
from app.schemas.user import QuestAssignmentInfo, UserFullInfo
from app.utils.dependencies import (
    get_current_user,
    require_company_admin,
    require_admin_or_hr,
)

router = APIRouter()

# Получить текущего пользователя
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# Регистрация нового пользователя
@router.post("/", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    user = create_user(db, user_in)
    user.role = "user"
    db.commit()
    db.refresh(user)
    return user

# Получить всех пользователей (только admin)
@router.get("/all", response_model=List[UserFullInfo])
def read_all_users(db: Session = Depends(get_db), _: User = Depends(require_company_admin)):
    users = db.query(User).options(
        joinedload(User.employee).joinedload(Employee.company),
        joinedload(User.employee).joinedload(Employee.assigned_quests)
    ).all()

    result = []
    for u in users:
        emp = u.employee
        assigned = [
            QuestAssignmentInfo(quest_id=qa.template_id, completed=qa.completed)            for qa in (emp.assigned_quests if emp else [])
        ]
        result.append(UserFullInfo(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            company=emp.company.name if emp and emp.company else None,
            role=u.role,
            position=emp.position if emp else None,
            department=emp.department if emp else None,
            employee_id=emp.id if emp else None,
            assigned_quests=assigned,
            is_mentor=(u.role == "mentor")
        ))
    return result

# Получить всех пользователей по компании (admin и hr)
@router.get("/by_company", response_model=list[UserResponse])
def read_users_by_company(current_user: User = Depends(require_admin_or_hr)):
    if not current_user.company:
        raise HTTPException(status_code=400, detail="У пользователя не указана компания")
    return get_users_by_company(current_user.company)

# Получить список пользователей (общий — с правами)
@router.get("/", response_model=List[UserResponse])
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("super_admin", "admin", "hr"):
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа")
    return db.query(User).all()

# Получить пользователя по ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin_or_hr)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

# Обновить пользователя
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_data: UserUpdate,
    current_user: User = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for field, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Удалить пользователя
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin_or_hr),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    employee = db.query(Employee).filter(Employee.user_id == user_id).first()
    if employee:
        db.delete(employee)

    db.delete(user)
    db.commit()


@router.put("/{user_id}/role", response_model=UserResponse)
def assign_role_to_user(
    user_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_roles = {
        "super_admin": ["super_admin", "company_admin", "hr", "manager", "mentor", "employee", "user"],
        "company_admin": ["company_admin", "hr", "manager", "mentor", "employee", "user"],
        "hr": ["super_admin","manager", "mentor", "employee", "user"],
        "manager": ["mentor"],
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if role_data.role not in allowed_roles[current_user.role]:
        raise HTTPException(status_code=403, detail="Вы не можете назначить эту роль")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user