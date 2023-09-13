import os
from fastapi import FastAPI, HTTPException, Depends, Cookie, Query, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, session, sessionmaker
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta

from .models.users_db import UserDB
from .models.sqlite_model import Item


app = FastAPI()

SECRET_KEY = "MY_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Подключаемся к БД "db_name" при помощи фабрики (тк Depends ожидает ссылку).
def get_db(db_name):
    def get_db_data():
        # Создаем путь к файлу базы данных в текущем каталоге.
        current_directory = os.path.dirname(os.path.abspath(__file__))
        database_file = os.path.join(current_directory, db_name)

        DATABASE_URL = f"sqlite:///{database_file}"
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    return get_db_data

# Функция для регистрации пользователя.
def user_registration(username: str, password: str, db: Session):
    hashed_password = bcrypt.hash(password)
    db_user = UserDB(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

# Маршрут для регистрации пользователя.
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db('users_db.db'))):
    user_registration(username, password, db)
    return {'Succesfull': f'User {username} registrated'}
    
# Функция для аутентификации.
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not bcrypt.verify(password, user.password):
        return None
    return user

# Маршрут для аутентификации и выдачи токена.
@app.post("/token")
async def login_for_access_token(username: str, password: str, db: Session = Depends(get_db('users_db.db'))):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Генерация токена.
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Функция для создания токена.
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для проверки текущего пользователя.
def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db('users_db.db'))):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Маршрут для получения данных за указанный период.
@app.get("/get_data")
async def get_data(
    date_from: datetime,
    date_to: datetime,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db('mydatabase.db'))
):
    data = db.query(Item).filter(
        Item.date >= date_from,
        Item.date <= date_to,
    ).all()

    result = [{"date": item.date, "is_active": item.is_active, "is_deleted": item.is_deleted} for item in data]
    return result
