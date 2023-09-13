import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.users_db import UserDB, Base


# Создаем путь к файлу базы данных в текущем каталоге.
current_directory = os.path.dirname(os.path.abspath(__file__))
database_file = os.path.join(current_directory, "users_db.db")

# Удаляем файл базы данных, если он существует.
if os.path.exists(database_file):
    os.remove(database_file)

# Создаем базу данных SQLite и соединение с ней.
DATABASE_URL = f"sqlite:///{database_file}"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()
item = UserDB(username='test', password='test')
session.add(item)
session.commit()
