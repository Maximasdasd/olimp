from tests.helpers import login


def test_student_register_for_olympiad(client, admin_headers):
    """Полный сценарий: преподаватель -> студент -> олимпиада -> запись."""
    teacher = client.post("/api/admin/teachers", headers=admin_headers, json={
        "email": "teacher_s@example.com",
        "username": "teacher_s",
        "password": "pass123",
        "full_name": "Преподаватель С",
        "department": "ИТ",
        "position": "Преподаватель",
    }).json()
    teacher_headers = {"Authorization": f"Bearer {login(client, 'teacher_s', 'pass123')}"}

    client.post("/api/teacher/students", headers=teacher_headers, json={
        "email": "student_s@example.com",
        "username": "student_s",
        "password": "pass123",
        "full_name": "Студент С",
        "institution": "ЕМК",
        "education_level": "СПО",
        "course": 2,
        "specialty": "ИП",
    })
    student_headers = {"Authorization": f"Bearer {login(client, 'student_s', 'pass123')}"}

    olymp = client.post("/api/admin/olympiads", headers=admin_headers, json={
        "title": "Олимпиада для записи",
        "year": 2025,
        "start_date": "2025-05-01",
        "end_date": "2025-05-02",
        "level": "Городская",
        "teacher_id": teacher["id"],
    }).json()

    resp = client.post(f"/api/student/register/{olymp['id']}", headers=student_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["olympiad_id"] == olymp["id"]

    # Повторная запись -> ошибка
    resp = client.post(f"/api/student/register/{olymp['id']}", headers=student_headers)
    assert resp.status_code == 400

    resp = client.get("/api/student/my-olympiads", headers=student_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_student_update_profile(client, admin_headers):
    """Студент редактирует свой профиль."""
    client.post("/api/admin/teachers", headers=admin_headers, json={
        "email": "teacher_p@example.com",
        "username": "teacher_p",
        "password": "pass123",
        "full_name": "Преп П",
        "department": "ИТ",
        "position": "Преп",
    })
    teacher_headers = {"Authorization": f"Bearer {login(client, 'teacher_p', 'pass123')}"}

    client.post("/api/teacher/students", headers=teacher_headers, json={
        "email": "student_p@example.com",
        "username": "student_p",
        "password": "pass123",
        "full_name": "Студент П",
        "institution": "ЕМК",
        "education_level": "СПО",
        "course": 1,
        "specialty": "ИП",
    })
    student_headers = {"Authorization": f"Bearer {login(client, 'student_p', 'pass123')}"}

    resp = client.put("/api/student/profile", headers=student_headers, json={"course": 4})
    assert resp.status_code == 200, resp.text
    assert resp.json()["course"] == 4


def test_student_endpoint_requires_auth(client):
    resp = client.get("/api/student/my-olympiads")
    assert resp.status_code == 401
