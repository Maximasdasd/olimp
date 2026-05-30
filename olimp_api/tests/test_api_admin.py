def test_create_teacher(client, admin_headers):
    """Тест создания преподавателя администратором"""
    response = client.post("/api/admin/teachers", json={
        "user": {
            "email": "new_teacher@example.com",
            "username": "new_teacher",
            "password": "teacher123",
            "full_name": "Новый Преподаватель",
            "role": "teacher"
        },
        "department": "Тестовый факультет",
        "position": "Доцент",
        "academic_degree": "Кандидат наук"
    }, headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "new_teacher"
    assert data["department"] == "Тестовый факультет"

def test_get_teachers(client, admin_headers):
    """Тест получения списка преподавателей"""
    response = client.get("/api/admin/teachers", headers=admin_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_olympiad_as_admin(client, admin_headers):
    """Тест создания олимпиады администратором"""
    response = client.post("/api/admin/olympiads", json={
        "title": "Админская Олимпиада",
        "description": "Создана администратором",
        "year": 2024,
        "start_date": "2024-12-20",
        "end_date": "2024-12-21",
        "registration_deadline": "2024-12-10",
        "location": "Тестовый город",
        "level": "всероссийская",
        "status": "planned",
        "teacher_id": 1
    }, headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Админская Олимпиада"
    assert data["creator_id"] is not None

def test_get_protocols_as_admin(client, admin_headers):
    """Тест получения протоколов администратором"""
    response = client.get("/api/admin/protocols", headers=admin_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)