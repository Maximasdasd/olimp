"""Вспомогательные функции для тестов (без побочных эффектов при импорте)."""


def login(client, username: str, password: str) -> str:
    """Вход через форму username/password, возвращает access-токен."""
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_headers(client, username: str, password: str) -> dict:
    return {"Authorization": f"Bearer {login(client, username, password)}"}
