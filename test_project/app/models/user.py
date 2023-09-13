from pydantic import BaseModel


# Модель данных для пользователей
class User(BaseModel):
    username: str
    password: str
