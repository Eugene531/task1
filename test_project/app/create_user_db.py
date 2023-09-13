import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.users_db import UserDB, Base


# Определяем путь к текущему каталогу, где находится файл Python.
current_directory = os.path.dirname(os.path.abspath(__file__))

# Создаем путь к файлу базы данных в текущем каталоге.
database_file = os.path.join(current_directory, "users_db.db")

# Удаляем файл базы данных, если он существует.
if os.path.exists(database_file):
    os.remove(database_file)

# Создаем базу данных SQLite и соединение с ней, используя полученный путь.
DATABASE_URL = f"sqlite:///{database_file}"
engine = create_engine(DATABASE_URL)

# Создаем таблицу в базе данных.
Base.metadata.create_all(bind=engine)

# Создаем сессию для взаимодействия с базой данных.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем сессию для взаимодействия с базой данных.
session = SessionLocal()
item = UserDB(username='test', password='test')
session.add(item)
session.commit()
