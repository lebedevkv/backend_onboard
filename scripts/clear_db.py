#!/usr/bin/env python3
# scripts/clear_db.py

import os
import sys
from sqlalchemy import create_engine, text

def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Ошибка: задайте переменную окружения DATABASE_URL")
        sys.exit(1)

    engine = create_engine(db_url)
    with engine.begin() as conn:
        # Удаляем всю схему public и создаём заново
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        print("Схема public сброшена и пересоздана.")

    print("База очищена от старых данных.")

if __name__ == "__main__":
    main()