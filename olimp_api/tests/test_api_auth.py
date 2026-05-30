def test_register_user(client):
    """Регистрация нового пользователя возвращает токен."""
    response = client.post("/api/auth/register", json={
        "email": "new_user@example.com",
        "username": "new_user",
        "password": "password123",
        "full_name": "Новый Пользователь",
        "role": "student",
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "new_user"
    assert data["role"] == "student"


def test_login_success(client):
    """Вход по логину и паролю (форма)."""
    client.post("/api/auth/register", json={
        "email": "login_test@example.com",
        "username": "login_test",
        "password": "test123",
        "full_name": "Тест Логин",
        "role": "student",
    })
    # Логин отправляется как форма (data=), а не JSON
    response = client.post("/api/auth/login", data={
        "username": "login_test",
        "password": "test123",
    })
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    """Вход с неправильным паролем -> 401."""
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "wrong_password",
    })
    assert response.status_code == 401


def test_get_current_user(client, admin_headers):
    """Получение информации о текущем пользователе."""
    response = client.get("/api/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_me_requires_auth(client):
    """Без токена /me возвращает 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
