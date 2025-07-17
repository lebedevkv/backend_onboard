from app.db.session import SessionLocal
from app.models.user import User

def clear_users():
    db = SessionLocal()
    try:
        deleted = db.query(User).delete()
        db.commit()
        print(f"✅ Удалено пользователей: {deleted}")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при удалении: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_users()