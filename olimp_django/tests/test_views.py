"""
Тесты Django-вьюх фронтенда «Олимпиадное движение».

FastAPI замокан (фикстура mock_fastapi), поэтому тесты детерминированы и не
требуют запущенного бэкенда. Покрывают:
  * публичные страницы;
  * редиректы на логин без токена;
  * проверку прав по ролям;
  * рендер страниц для каждой роли и заголовки;
  * вход, регистрацию, выход.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db  # сессии Django используют БД


# ──────────────────────────────────────────────
#  Публичные страницы
# ──────────────────────────────────────────────
class TestPublicPages:
    def test_olympiad_list_ok(self, client, mock_fastapi):
        mock_fastapi.set_get_default([
            {"id": 1, "title": "Олимпиада А", "year": 2025,
             "level": "Региональная", "is_protocol_published": True},
        ])
        response = client.get(reverse("olympiad_list"))
        assert response.status_code == 200
        assert "Олимпиада А" in response.content.decode("utf-8")

    def test_olympiad_list_title(self, client, mock_fastapi):
        response = client.get(reverse("olympiad_list"))
        assert "Олимпиады" in response.content.decode("utf-8")

    def test_olympiad_detail_ok(self, client, mock_fastapi):
        mock_fastapi.set_get("/api/olympiads/1", {
            "id": 1, "title": "Олимпиада Б", "year": 2025,
            "is_protocol_published": True,
        })
        mock_fastapi.set_get("/api/olympiads/1/results", [
            {"place": 1, "student_id": 7, "score": 95, "result_type": "winner"},
        ])
        response = client.get(reverse("olympiad_detail", args=[1]))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Олимпиада Б" in content
        assert "winner" in content

    def test_olympiad_detail_not_found_redirects(self, client, mock_fastapi):
        mock_fastapi.set_get("/api/olympiads/999", {"detail": "not found"}, status=404)
        response = client.get(reverse("olympiad_detail", args=[999]))
        assert response.status_code == 302


# ──────────────────────────────────────────────
#  Доступ без токена → редирект на логин
# ──────────────────────────────────────────────
class TestAuthRedirects:
    @pytest.mark.parametrize("route", [
        "profile", "teacher_dashboard", "admin_dashboard",
        "create_protocol", "create_olympiad", "create_teacher", "create_student",
    ])
    def test_protected_pages_redirect_to_login(self, client, mock_anon, route):
        response = client.get(reverse(route))
        assert response.status_code == 302
        assert "/login/" in response.url


# ──────────────────────────────────────────────
#  Контроль доступа по ролям
# ──────────────────────────────────────────────
class TestRolePermissions:
    def test_student_cannot_open_admin(self, student_client, mock_fastapi):
        mock_fastapi.set_role("student")
        response = student_client.get(reverse("admin_dashboard"))
        assert response.status_code == 302  # редирект со «Недостаточно прав»

    def test_student_cannot_open_teacher(self, student_client, mock_fastapi):
        mock_fastapi.set_role("student")
        response = student_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 302

    def test_teacher_cannot_open_admin(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        response = teacher_client.get(reverse("admin_dashboard"))
        assert response.status_code == 302

    def test_admin_can_open_teacher(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        response = admin_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Студент
# ──────────────────────────────────────────────
class TestStudentPages:
    def test_profile_ok(self, student_client, mock_fastapi):
        mock_fastapi.set_role("student")
        response = student_client.get(reverse("profile"))
        assert response.status_code == 200
        assert "Мой профиль" in response.content.decode("utf-8")


# ──────────────────────────────────────────────
#  Преподаватель
# ──────────────────────────────────────────────
class TestTeacherPages:
    def test_dashboard_ok(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        response = teacher_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 200
        assert "Кабинет преподавателя" in response.content.decode("utf-8")

    def test_student_create_form_ok(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        response = teacher_client.get(reverse("create_student"))
        assert response.status_code == 200
        assert "студента" in response.content.decode("utf-8")


# ──────────────────────────────────────────────
#  Администратор
# ──────────────────────────────────────────────
class TestAdminPages:
    def test_dashboard_ok(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        response = admin_client.get(reverse("admin_dashboard"))
        assert response.status_code == 200
        assert "Панель администратора" in response.content.decode("utf-8")

    def test_olympiad_create_form_ok(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        response = admin_client.get(reverse("create_olympiad"))
        assert response.status_code == 200

    def test_teacher_create_form_ok(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        response = admin_client.get(reverse("create_teacher"))
        assert response.status_code == 200
        assert "преподавателя" in response.content.decode("utf-8")


# ──────────────────────────────────────────────
#  Вход / регистрация / выход
# ──────────────────────────────────────────────
class TestLogin:
    def test_login_page_ok(self, client, mock_anon):
        response = client.get(reverse("login"))
        assert response.status_code == 200
        assert "Вход" in response.content.decode("utf-8")

    def test_login_success_sets_token_and_redirects(self, client, mock_fastapi):
        response = client.post(reverse("login"), {
            "username": "admin", "password": "admin123",
        })
        assert response.status_code == 302
        assert client.session.get("fastapi_token") == "test-token-123"

    def test_login_failure_renders_login(self, client, monkeypatch):
        import core.fastapi_client as fc

        class R:
            status_code = 401
            def json(self):
                return {"detail": "Неверное имя пользователя или пароль"}
        # /api/auth/me -> 401 (аноним), /api/auth/login -> 401
        monkeypatch.setattr(fc.requests, "get", lambda *a, **k: R())
        monkeypatch.setattr(fc.requests, "post", lambda *a, **k: R())
        response = client.post(reverse("login"), {
            "username": "admin", "password": "wrong",
        })
        assert response.status_code == 200
        assert client.session.get("fastapi_token") is None


class TestRegister:
    def test_register_page_ok(self, client, mock_anon):
        response = client.get(reverse("register"))
        assert response.status_code == 200
        assert "Регистрация" in response.content.decode("utf-8")

    def test_register_success_redirects(self, client, mock_fastapi):
        response = client.post(reverse("register"), {
            "username": "newbie", "full_name": "Новиков Н.Н.",
            "email": "n@example.com", "password": "Pass123word",
        })
        assert response.status_code == 302
        assert client.session.get("fastapi_token") == "test-token-123"


class TestLogout:
    def test_logout_redirects_and_clears(self, auth_client, mock_fastapi):
        response = auth_client.get(reverse("logout"))
        assert response.status_code == 302
        assert auth_client.session.get("fastapi_token") is None
