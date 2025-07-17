import shutil
import sys

if not shutil.which("dot"):
    print("❌ Graphviz (dot) не найден. Установите его:\n  • brew install graphviz (macOS)\n  • apt install graphviz (Ubuntu)\n  • https://graphviz.org/download/")
    sys.exit(1)

from sqlalchemy import create_engine, MetaData
from sqlalchemy_schemadisplay import create_schema_graph

# Строка подключения к вашей БД (пример: SQLite)
engine = create_engine("postgresql://postgres:postgres@localhost/hr_platform")  # Замените на свою БД, если нужно

# Рефлексия существующих таблиц
metadata = MetaData()
metadata.reflect(bind=engine)

# Создание графа
graph = create_schema_graph(
    metadata=metadata,
    engine=engine,
    show_datatypes=True,    # показывать типы столбцов
    show_indexes=True,      # показывать индексы
    rankdir='LR',           # направление Left-to-Right
    concentrate=False
)

# Сохранение в PNG
graph.write_png('er_diagram.png')

#PYTHONPATH=. python scripts/generate_er.py