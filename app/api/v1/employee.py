from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate, UserResponse
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.employee_service import create_employee, get_employee_by_id, get_all_employees, get_users_by_company
from app.utils.dependencies import get_current_user, require_roles

router = APIRouter()

@router.post("/", response_model=EmployeeRead)
def create_new_employee(
    data: EmployeeCreate
    ,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["hr", "company_admin", "super_admin"]))
):
    employee = create_employee(db, data)
    user = db.query(User).get(employee.user_id)
    user.company_id = employee.company_id
    user.employee_id = employee.id
    user.role = "employee"
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/", response_model=list[EmployeeRead])
def list_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["hr", "company_admin", "super_admin"]))
):
    return get_all_employees(db, current_user.company_id)

@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# Endpoint to delete employee
@router.delete("/{employee_id}", response_model=EmployeeRead)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["hr", "company_admin", "super_admin"]))
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    from app.services.employee_service import delete_employee as delete_employee_service
    return delete_employee_service(db, employee_id)

@router.put("/{employee_id}/supervisor/{supervisor_id}", response_model=EmployeeRead)
def assign_supervisor_to_employee(
    employee_id: int,
    supervisor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["hr", "company_admin", "super_admin"]))
):
    from app.services.employee_service import assign_supervisor
    return assign_supervisor(db, employee_id, supervisor_id)

@router.delete("/{employee_id}/supervisor", response_model=EmployeeRead)
def remove_supervisor_from_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["hr", "company_admin", "super_admin"]))
):
    from app.services.employee_service import remove_supervisor
    return remove_supervisor(db, employee_id)

@router.get("/by-company/{company_id}", response_model=list[UserResponse])
def list_employees_by_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # здесь проверка прав текущего пользователя, если нужно
    users = get_users_by_company(db, company_id)
    return users