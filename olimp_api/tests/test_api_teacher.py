import pytest

@pytest.fixture
def teacher_token(client):
    """Создаем и получаем токен преподавателя"""
    # Создаем преподавателя через админа
    admin_response = client.post("/api/auth/login", json={
        "username": "test_admin",
        "password": "test123"
    })
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Создаем преподавателя
    client.post("/api/admin/teachers", json={
        "user": {
            "email": "test_teacher@example.com",
            "username": "test_teacher",
            "password": "teacher123",
            "full_name": "Тестовый Преподаватель",
            "role": "teacher"
        },
        "department": "Тестовый",
        "position": "Преподаватель",
        "academic_degree": ""
    }, headers=admin_headers)
    
    # Логинимся как преподаватель
    response = client.post("/api/auth/login", json={
        "username": "test_teacher",
        "password": "teacher123"
    })
    return response.json()["access_token"]

@pytest.fixture
def teacher_headers(teacher_token):
    return {"Authorization": f"Bearer {teacher_token}"}

def test_create_student_as_teacher(client, teacher_headers):
    """Тест создания студента преподавателем"""
    response = client.post("/api/teacher/students", json={
        "user": {
            "email": "teacher_created@example.com",
            "username": "teacher_student",
            "password": "student123",
            "full_name": "Студент от преподавателя",
            "role": "student"
        },
        "birth_date": "2000-01-01",
        "phone": "+79001234567",
        "institution": "Тестовый университет",
        "education_level": "бакалавриат",
        "course": 3,
        "specialty": "тестирование"
    }, headers=teacher_headers)
    
    assert response.status_code == 200
    assert "student_id" in response.json()