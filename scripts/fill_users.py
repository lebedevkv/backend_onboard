from app.db.session import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

def fill_users():
    db = SessionLocal()
    try:
        users = [
            # 👑 Супер админ
            User(
                full_name="Супер Админ",
                email="superadmin@example.com",
                hashed_password=hash_password("superpass"),
                role="super_admin",
                is_active=True,
                company="ООО Рога и Копыта",
                department="Администрация1",
                position="Супер Админ"
            ),
            # 🏢 Админ компании
            User(
                full_name="Админ Компании",
                email="companyadmin@example.com",
                hashed_password=hash_password("companypass"),
                role="company_admin",
                is_active=True,
                company="ООО Рога и Копыта",
                department="Администрация",
                position="Администратор"
            ),
            # 👩‍💼 HR (2)
            User(
                full_name="HR Один",
                email="hr1@example.com",
                hashed_password=hash_password("hrpass1"),
                role="hr",
                is_active=True,
                company="ООО Рога и Копыта",
                department="Отдел кадров",
                position="HR специалист"
            ),
            User(
                full_name="HR Два",
                email="hr2@example.com",
                hashed_password=hash_password("hrpass2"),
                role="hr",
                is_active=True,
                company="ООО Рога и Копыта",
                department="Отдел кадров",
                position="HR менеджер"
            ),
            # 👨‍💼 Менеджеры (4)
            *[
                User(
                    full_name=f"Менеджер {i}",
                    email=f"manager{i}@example.com",
                    hashed_password=hash_password(f"managerpass{i}"),
                    role="manager",
                    is_active=True,
                    company="ООО Рога и Копыта",
                    department="Проекты",
                    position="Менеджер проекта"
                ) for i in range(1, 5)
            ],
            # 👷‍♂️ Сотрудники (10)
            *[
                User(
                    full_name=f"Сотрудник {i}",
                    email=f"user{i}@example.com",
                    hashed_password=hash_password(f"userpass{i}"),
                    role="employee",
                    is_active=True,
                    company="ООО Рога и Копыта",
                    department="Производство",
                    position="Инженер"
                ) for i in range(1, 11)
            ]
        ]

        db.add_all(users)
        db.commit()
        print("✅ Пользователи успешно добавлены.")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fill_users()