import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models.sqlite_model import Item, Base


# Определяем путь к текущему каталогу, где находится файл Python.
current_directory = os.path.dirname(os.path.abspath(__file__))

# Создаем путь к файлу базы данных в текущем каталоге.
database_file = os.path.join(current_directory, "mydatabase.db")

# Удаляем файл базы данных, если он существует.
if os.path.exists(database_file):
    os.remove(database_file)

# Создаем базу данных SQLite и соединение с ней, используя полученный путь.
DATABASE_URL = f"sqlite:///{database_file}"
engine = create_engine(DATABASE_URL)

# Создаем таблицы в базе данных.
Base.metadata.create_all(bind=engine)

# Создаем сессию для взаимодействия с базой данных.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Заполняем базу данных данными.
data_to_insert = [
    {"date": datetime(2023, 1, 15), "is_active": False, "is_deleted": False},
    {"date": datetime(2023, 3, 23), "is_active": False, "is_deleted": True},
    {"date": datetime(2023, 4, 11), "is_active": True, "is_deleted": False},
    {"date": datetime(2023, 6, 10), "is_active": True, "is_deleted": True},
]

for item_data in data_to_insert:
    item = Item(**item_data)
    session.add(item)

session.commit()
