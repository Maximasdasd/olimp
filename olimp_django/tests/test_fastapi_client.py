"""
Тесты модуля core/fastapi_client.py — клиента к FastAPI-бэкенду.

Проверяемые функции:
  * get_fastapi_token(request)      — токен из сессии (или None);
  * get_headers(request)            — заголовок Authorization (или {});
  * login_to_fastapi(request, ...)  — логин в FastAPI, токен в сессию;
  * register_student(request, ...)  — регистрация студента;
  * logout(request)                 — очистка сессии.
"""
from unittest.mock import patch

from core.fastapi_client import (
    get_fastapi_token, get_headers, login_to_fastapi, register_student, logout,
)


class FakeSessionRequest:
    """Минимальный объект request с атрибутом session (dict)."""
    def __init__(self, session=None):
        self.session = session if session is not None else {}


class FakeResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = str(self._json)

    def json(self):
        return self._json


# ──────────────────────────────────────────────
#  get_fastapi_token
# ──────────────────────────────────────────────
class TestGetToken:
    def test_returns_token_when_present(self):
        req = FakeSessionRequest({"fastapi_token": "abc123"})
        assert get_fastapi_token(req) == "abc123"

    def test_returns_none_when_absent(self):
        req = FakeSessionRequest({})
        assert get_fastapi_token(req) is None


# ──────────────────────────────────────────────
#  get_headers
# ──────────────────────────────────────────────
class TestGetHeaders:
    def test_headers_with_token(self):
        req = FakeSessionRequest({"fastapi_token": "abc123"})
        assert get_headers(req) == {"Authorization": "Bearer abc123"}

    def test_headers_without_token(self):
        req = FakeSessionRequest({})
        assert get_headers(req) == {}


# ──────────────────────────────────────────────
#  login_to_fastapi
# ──────────────────────────────────────────────
class TestLogin:
    @patch("core.fastapi_client.requests.post")
    def test_login_success_saves_token(self, mock_post):
        mock_post.return_value = FakeResponse({
            "access_token": "tok", "token_type": "bearer",
            "user_id": 1, "username": "admin", "role": "admin",
        }, 200)
        req = FakeSessionRequest()
        ok, error = login_to_fastapi(req, "admin", "admin123")
        assert ok is True
        assert error is None
        assert req.session["fastapi_token"] == "tok"
        assert req.session["user_info"]["role"] == "admin"

    @patch("core.fastapi_client.requests.post")
    def test_login_sends_form_data(self, mock_post):
        """Логин отправляется как form-data (data=...), а не json."""
        mock_post.return_value = FakeResponse({"access_token": "tok"}, 200)
        login_to_fastapi(FakeSessionRequest(), "u", "p")
        _, kwargs = mock_post.call_args
        assert "data" in kwargs
        assert kwargs["data"]["username"] == "u"
        assert kwargs["data"]["password"] == "p"

    @patch("core.fastapi_client.requests.post")
    def test_login_failure_no_token(self, mock_post):
        mock_post.return_value = FakeResponse({"detail": "Неверный пароль"}, 401)
        req = FakeSessionRequest()
        ok, error = login_to_fastapi(req, "admin", "wrong")
        assert ok is False
        assert "fastapi_token" not in req.session
        assert "Неверный" in error


# ──────────────────────────────────────────────
#  register_student
# ──────────────────────────────────────────────
class TestRegister:
    @patch("core.fastapi_client.requests.post")
    def test_register_success_logs_in(self, mock_post):
        mock_post.return_value = FakeResponse({
            "access_token": "tok", "user_id": 5,
            "username": "newbie", "role": "student",
        }, 200)
        req = FakeSessionRequest()
        ok, error = register_student(req, {"username": "newbie"})
        assert ok is True
        assert req.session["fastapi_token"] == "tok"

    @patch("core.fastapi_client.requests.post")
    def test_register_sends_json(self, mock_post):
        """Регистрация отправляется как JSON."""
        mock_post.return_value = FakeResponse({"access_token": "t"}, 200)
        register_student(FakeSessionRequest(), {"username": "x"})
        _, kwargs = mock_post.call_args
        assert "json" in kwargs
        assert kwargs["json"]["username"] == "x"


# ──────────────────────────────────────────────
#  logout
# ──────────────────────────────────────────────
class TestLogout:
    def test_logout_clears_session(self):
        req = FakeSessionRequest({"fastapi_token": "tok", "user_info": {"role": "admin"}})
        logout(req)
        assert "fastapi_token" not in req.session
        assert "user_info" not in req.session
