def test_list_olympiads(client):
    """Список олимпиад доступен без авторизации."""
    response = client.get("/api/olympiads")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_olympiad_not_found(client):
    """Несуществующая олимпиада -> 404."""
    response = client.get("/api/olympiads/999999")
    assert response.status_code == 404


def test_root(client):
    """Корневой эндпоинт отвечает."""
    response = client.get("/")
    assert response.status_code == 200
