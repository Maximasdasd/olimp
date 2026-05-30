def test_register_user(client):
    """Тест регистрации пользователя"""
    response = client.post("/api/auth/register", json={
        "email": "new_user@example.com",
        "username": "new_user",
        "password": "password123",
        "full_name": "Новый Пользователь",
        "role": "student"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "new_user"
    assert data["user"]["email"] == "new_user@example.com"

def test_login_success(client):
    """Тест успешного входа"""
    # Сначала регистрируем
    client.post("/api/auth/register", json={
        "email": "login_test@example.com",
        "username": "login_test",
        "password": "test123",
        "full_name": "Тест Логин",
        "role": "student"
    })
    
    # Пытаемся войти
    response = client.post("/api/auth/login", json={
        "username": "login_test",
        "password": "test123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "login_test"

def test_login_wrong_password(client):
    """Тест входа с неправильным паролем"""
    response = client.post("/api/auth/login", json={
        "username": "test_admin",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert "Неверное имя пользователя или пароль" in response.json()["detail"]

def test_get_current_user(client, admin_headers):
    """Тест получения информации о текущем пользователе"""
    response = client.get("/api/auth/me", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_admin"
    assert data["role"] == "admin"