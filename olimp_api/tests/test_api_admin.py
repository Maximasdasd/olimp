def test_create_teacher_and_olympiad(client, admin_headers):
    """Администратор создает преподавателя и олимпиаду."""
    resp = client.post("/api/admin/teachers", headers=admin_headers, json={
        "email": "teacher_a@example.com",
        "username": "teacher_a",
        "password": "pass123",
        "full_name": "Преподаватель А",
        "department": "ИТ",
        "position": "Доцент",
    })
    assert resp.status_code == 200, resp.text
    teacher_id = resp.json()["id"]

    resp = client.post("/api/admin/olympiads", headers=admin_headers, json={
        "title": "Олимпиада по программированию",
        "description": "Тест",
        "year": 2025,
        "start_date": "2025-03-01",
        "end_date": "2025-03-02",
        "level": "Городская",
        "teacher_id": teacher_id,
    })
    assert resp.status_code == 200, resp.text
    assert resp.json()["title"] == "Олимпиада по программированию"


def test_admin_endpoint_requires_auth(client):
    """Эндпоинт администратора без токена -> 401."""
    resp = client.get("/api/admin/protocols")
    assert resp.status_code == 401


def test_admin_list_protocols(client, admin_headers):
    """Администратор видит список протоколов."""
    resp = client.get("/api/admin/protocols", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
