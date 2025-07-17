from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import create_access_token

from rich import print

def print_users_by_roles():
    db: Session = SessionLocal()
    roles = ["super_admin", "company_admin", "hr", "manager", "mentor", "employee"]
    for role in roles:
        user = db.query(User).filter(User.role == role).first()
        if user:
            token = create_access_token(user_id=user.id, email=user.email)
            print(f"[bold]{role}[/bold]")
            print(f"  ID пользователя: {user.id}")
            print(f"  ID сотрудника: {user.employee_id}")
            print(f"  Логин (email): {user.email}")
            print(f"  Пароль Hash: {user.hashed_password}")
            print(f"  Компания: {user.company.name if user.company else '—'}")
            print(f"  Компания: {user.company_id}")
            print(f"  Должность: {user.position}")
            print(f"  Отдел: {user.department}")
            print(f"  JWT: [green]{token}[/green]\n")
        else:
            print(f"[bold red]{role}[/bold red] — пользователь не найден\n")

    db.close()

if __name__ == "__main__":
    print_users_by_roles()

#PYTHONPATH=. python scripts/print_user.py
