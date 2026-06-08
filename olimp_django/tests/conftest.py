"""
conftest.py — фикстуры для тестов Django-фронтенда «Олимпиадное движение».

Архитектура проекта:
  * Django — фронтенд, данные и аутентификация берутся из FastAPI-бэкенда;
  * пользователь логинится через /login/ -> Django шлёт логин/пароль в FastAPI;
  * FastAPI возвращает JWT, Django кладёт его в сессию (request.session['fastapi_token']);
  * все страницы тянут данные из FastAPI через requests.* с этим токеном.

Поэтому НЕ используются User.objects.create_user / client.login(). Вместо этого:
  * фикстура `auth_client` кладёт токен прямо в сессию;
  * фикстура `mock_fastapi` подменяет requests.* в core.fastapi_client, чтобы
    тесты не ходили в реальный FastAPI.
"""
import pytest
from django.test import Client


# --- ALLOWED_HOSTS -------------------------------------------------------
@pytest.fixture(autouse=True)
def _allow_testserver(settings):
    settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]


# --- Клиенты -------------------------------------------------------------
@pytest.fixture
def client():
    """Анонимный Django test client (без токена FastAPI в сессии)."""
    return Client()


def _make_auth_client(role, username):
    client = Client()
    session = client.session
    session["fastapi_token"] = "test-token-123"
    session["user_info"] = {"id": 1, "username": username, "role": role}
    session.save()
    return client


@pytest.fixture
def auth_client():
    """Клиент с «залогиненным» пользователем (роль студента по умолчанию)."""
    return _make_auth_client("student", "student")


@pytest.fixture
def student_client():
    return _make_auth_client("student", "student")


@pytest.fixture
def teacher_client():
    return _make_auth_client("teacher", "teacher")


@pytest.fixture
def admin_client():
    return _make_auth_client("admin", "admin")


# --- Мок ответов FastAPI -------------------------------------------------
class FakeResponse:
    """Имитация requests.Response."""
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data if json_data is not None else {}
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = str(self._json)

    def json(self):
        return self._json


@pytest.fixture
def mock_fastapi(monkeypatch):
    """
    Подменяет HTTP-вызовы к FastAPI в core.fastapi_client на заглушки.

    По умолчанию:
      * GET возвращает 200 и пустой список (страницы-списки не падают);
      * /api/auth/me возвращает залогиненного пользователя (роль настраивается);
      * POST/PUT возвращают 200.
    Тест может донастроить поведение через возвращаемый объект-контроллер.
    """
    import core.fastapi_client as fc

    state = {
        "me": {"id": 1, "username": "user", "role": "student"},
        "get_default": FakeResponse([], 200),
        "get_map": {},   # path -> FakeResponse
        "post": FakeResponse({"detail": "ok"}, 200),
        "put": FakeResponse({"detail": "ok"}, 200),
    }

    def fake_get(url, headers=None, params=None, timeout=None):
        # /api/auth/me -> текущий пользователь
        if url.endswith("/api/auth/me"):
            return FakeResponse(state["me"], 200)
        for path, resp in state["get_map"].items():
            if url.endswith(path):
                return resp
        return state["get_default"]

    def fake_post(url, headers=None, json=None, data=None, timeout=None):
        # логин и регистрация: вернуть токен
        if url.endswith("/api/auth/login") or url.endswith("/api/auth/register"):
            return FakeResponse({
                "access_token": "test-token-123", "token_type": "bearer",
                "user_id": 1, "username": "user", "role": state["me"]["role"],
            }, 200)
        return state["post"]

    def fake_put(url, headers=None, json=None, timeout=None):
        return state["put"]

    monkeypatch.setattr(fc.requests, "get", fake_get)
    monkeypatch.setattr(fc.requests, "post", fake_post)
    monkeypatch.setattr(fc.requests, "put", fake_put)

    class Controller:
        Response = FakeResponse

        def set_role(self, role):
            state["me"]["role"] = role

        def set_get(self, path, json_data, status=200):
            state["get_map"][path] = FakeResponse(json_data, status)

        def set_get_default(self, json_data, status=200):
            state["get_default"] = FakeResponse(json_data, status)

        def set_post(self, json_data, status=200):
            state["post"] = FakeResponse(json_data, status)

        def set_put(self, json_data, status=200):
            state["put"] = FakeResponse(json_data, status)

    return Controller()


@pytest.fixture
def mock_anon(monkeypatch):
    """Мок без авторизации: /api/auth/me всегда возвращает 401."""
    import core.fastapi_client as fc

    def fake_get(url, headers=None, params=None, timeout=None):
        if url.endswith("/api/auth/me"):
            return FakeResponse({"detail": "unauth"}, 401)
        return FakeResponse([], 200)

    monkeypatch.setattr(fc.requests, "get", fake_get)
    return True
