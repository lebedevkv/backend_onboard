from sqlalchemy import text
from app.db.session import SessionLocal
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    print("✅ Подключение к БД успешно")
except Exception as e:
    print("❌ Ошибка подключения к БД:", e)
finally:
    db.close()