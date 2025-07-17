from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.employee import Employee
from tabulate import tabulate

def get_all_users_with_details(db: Session):
    users = db.query(User).all()
    rows = []
    for user in users:
        employee = getattr(user, "employee", None)
        rows.append({
            "ID": user.id,
            "Email": user.email,
            "Full Name": user.full_name,
            "Role": user.role,
            "Position": employee.position if employee else "",
            "Department": employee.department if employee else "",
            "Employee ID": employee.id if employee else "",
        })
    return rows

if __name__ == "__main__":
    db = SessionLocal()
    users_data = get_all_users_with_details(db)
    print(tabulate(users_data, headers="keys", tablefmt="grid"))


#PYTHONPATH=. python scripts/users_table.py