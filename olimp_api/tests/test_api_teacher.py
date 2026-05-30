import pytest
from tests.helpers import login


@pytest.fixture
def teacher_headers(client, admin_headers):
    """Создаем преподавателя через админа и входим под ним."""
    client.post("/api/admin/teachers", headers=admin_headers, json={
        "email": "teacher_b@example.com",
        "username": "teacher_b",
        "password": "pass123",
        "full_name": "Преподаватель Б",
        "department": "ИТ",
        "position": "Преподаватель",
    })
    token = login(client, "teacher_b", "pass123")
    return {"Authorization": f"Bearer {token}"}


def test_teacher_create_student(client, teacher_headers):
    """Преподаватель создает учетную запись студента."""
    resp = client.post("/api/teacher/students", headers=teacher_headers, json={
        "email": "student_b@example.com",
        "username": "student_b",
        "password": "pass123",
        "full_name": "Студент Б",
        "institution": "ЕМК",
        "education_level": "СПО",
        "course": 3,
        "specialty": "Информационные системы",
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["username"] == "student_b"


def test_teacher_create_protocol(client, admin_headers, teacher_headers):
    """Преподаватель создает протокол для олимпиады."""
    olymp = client.post("/api/admin/olympiads", headers=admin_headers, json={
        "title": "Олимпиада для протокола",
        "year": 2025,
        "start_date": "2025-04-01",
        "end_date": "2025-04-02",
        "level": "Региональная",
    }).json()

    resp = client.post("/api/teacher/protocols", headers=teacher_headers, json={
        "olympiad_id": olymp["id"],
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "draft"


def test_teacher_endpoint_requires_auth(client):
    resp = client.post("/api/teacher/protocols", json={"olympiad_id": 1})
    assert resp.status_code == 401
