import random
import string
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

# Для генерации случайного юзера
def generate_random_credentials():
    username = ''.join(random.choices(string.ascii_letters, k=32))
    password = ''.join(random.choices(string.ascii_letters, k=32))
    return username, password

def test_register_user():
    # Тест регистрации пользователя
    username, password = generate_random_credentials()
    response = client.post("/register", params={"username": username, "password": password})
    assert response.status_code == 200
    assert response.json() == {"Succesfull": f"User {username} registrated"}

def test_login_and_get_data():
    # Тест аутентификации
    username, password = generate_random_credentials()
    client.post("/register", params={"username": username, "password": password})

    # Тест получения токена
    response = client.post("/token", params={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Тест получения данных из БД
    response = client.get("/get_data", params={"date_from": "2022-01-01T00:00:00", "date_to": "2023-12-31T00:00:00"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_invalid_credentials():
    # Тест на неверные учетные данные
    username, password = generate_random_credentials()
    response = client.post("/token", params={"username": username, "password": f"WRONG{password}"})
    assert response.status_code == 400
    assert "Incorrect username or password" in response.text

def test_access_with_invalid_token():
    # Тест на невалидный токен
    username, password = generate_random_credentials()
    client.post("/register", params={"username": username, "password": password})

    response = client.post("/token", params={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Получение данных по невалидному токену
    response = client.get("/get_data", params={"date_from": "2022-01-01T00:00:00", "date_to": "2023-12-31T00:00:00"},
                          headers={"Authorization": f"Bearer WROND{token}"})
    assert response.status_code == 401

def test_access_with_invalid_parameters():
    # Тест на получение данных с недопустимыми параметрами
    username, password = generate_random_credentials()
    client.post("/register", params={"username": username, "password": password})

    response = client.get("/get_data", params={"date_from": "invalid_date", "date_to": "invalid_date"},
                          headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
