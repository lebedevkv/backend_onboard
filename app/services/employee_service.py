from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.employee import EmployeeCreate
from app.models.employee import Employee


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    user = db.query(User).filter(User.id == data.user_id).first()
    if not hasattr(data, "company_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing company_id in request data"
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db.query(Employee).filter(Employee.user_id == data.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already exists for this user"
        )

    employee = Employee(
        user_id=data.user_id,
        position=data.position,
        department=data.department,
        company_id=data.company_id
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    # Update user with employee-related fields
    user.position = data.position
    user.department = data.department
    user.company_id = data.company_id  # предполагается, что это поле есть в data
    user.employee_id = employee.id
    db.commit()
    db.refresh(user)
    return employee


def get_employee_by_id(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee


def get_all_employees(db: Session, company_id: int):
    # Получаем список сотрудников из базы
    employees = (
        db.query(Employee)
        .join(User, Employee.user_id == User.id)
        .filter(User.company_id == company_id)
        .all()
    )
    # Формируем результат: mentees как список id, а не объектов
    return [
        {
            "id": emp.id,
            "user_id": emp.user_id,
            "position": emp.position,
            "department": emp.department,
            "company_id": emp.company_id,
            "supervisor_id": emp.supervisor_id,
            "mentees": [mentee.id for mentee in emp.mentees]
        }
        for emp in employees
    ]



# Удаление сотрудника и сброс роли пользователя
def delete_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    user = db.query(User).filter(User.id == employee.user_id).first()
    if user:
        user.company_id = None
        user.position = None
        user.department = None
        user.employee_id = None
        user.role = "user"
        db.commit()
        db.refresh(user)

    db.delete(employee)
    db.commit()
    return {"detail": "Employee deleted and user reset to default role"}


def assign_supervisor(db: Session, employee_id: int, supervisor_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    supervisor = db.query(Employee).filter(Employee.id == supervisor_id).first()
    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supervisor not found"
        )
    # Prevent self-assignment
    if employee.id == supervisor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign employee as their own supervisor"
        )
    employee.supervisor_id = supervisor_id

    # Ensure reverse relationship
    supervisor.mentees.append(employee)

    # Mark supervisor's user as a mentor
    supervisor_user = supervisor.user
    if supervisor_user:
        supervisor_user.is_mentor = True

    db.commit()
    db.refresh(employee)
    db.refresh(supervisor)
    if supervisor_user:
        db.refresh(supervisor_user)

    return employee

def remove_supervisor(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    previous_supervisor_id = employee.supervisor_id
    employee.supervisor_id = None
    db.commit()
    db.refresh(employee)
    # Optionally demote supervisor if they have no more mentees
    if previous_supervisor_id:
        old_supervisor = db.query(Employee).filter(Employee.id == previous_supervisor_id).first()
        if old_supervisor and not old_supervisor.mentees:
            if old_supervisor.user:
                old_supervisor.user.is_mentor = False
                db.commit()
                db.refresh(old_supervisor.user)
    return employee

def get_users_by_company(db: Session, company_id: int) -> list[User]:
    """
    Return all User objects for employees belonging to the given company_id.
    """
    return (
        db.query(User)
        .join(Employee, Employee.user_id == User.id)
        .filter(Employee.company_id == company_id)
        .all()
    )