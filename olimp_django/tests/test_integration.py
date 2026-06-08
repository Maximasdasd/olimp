"""
Интеграционные тесты пользовательских сценариев Django-фронтенда.

Сквозные сценарии в рамках Django-слоя: вход → доступ к странице,
отправка формы → вызов FastAPI. Сам FastAPI замокан, чтобы тесты были
детерминированы и не требовали запущенного бэкенда.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestLoginFlow:
    """Вход и последующий доступ к защищённой странице."""

    def test_login_then_profile(self, client, mock_fastapi):
        mock_fastapi.set_role("student")
        # 1. логинимся (FastAPI-логин замокан -> токен в сессии)
        login_resp = client.post(reverse("login"), {
            "username": "student", "password": "student123",
        })
        assert client.session.get("fastapi_token") == "test-token-123"
        assert login_resp.status_code == 302

        # 2. теперь профиль доступен (200)
        profile = client.get(reverse("profile"))
        assert profile.status_code == 200

    def test_no_login_no_access(self, client, mock_anon):
        """Без входа защищённая страница ведёт на логин."""
        resp = client.get(reverse("profile"))
        assert resp.status_code == 302
        assert "/login/" in resp.url


class TestOlympiadRegistrationFlow:
    """Запись студента на олимпиаду → POST в FastAPI."""

    def test_register_for_olympiad_success(self, student_client, mock_fastapi):
        mock_fastapi.set_role("student")
        mock_fastapi.set_post({"id": 1, "olympiad_id": 1, "student_id": 1}, status=200)
        resp = student_client.post(reverse("register_for_olympiad", args=[1]))
        # после записи редирект на карточку
        assert resp.status_code == 302
        assert reverse("olympiad_detail", args=[1]) in resp.url


class TestTeacherCreatesStudentFlow:
    """Преподаватель создаёт учётную запись студента → POST в FastAPI."""

    def test_create_student(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        mock_fastapi.set_post({"id": 10, "username": "pupil"}, status=200)
        resp = teacher_client.post(reverse("create_student"), {
            "username": "pupil", "full_name": "Ученик У.У.",
            "email": "p@example.com", "password": "Pupil123",
            "institution": "ЕМК", "course": "2",
        })
        assert resp.status_code == 302


class TestAdminCreatesTeacherFlow:
    """Администратор создаёт учётную запись преподавателя → POST в FastAPI."""

    def test_create_teacher(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        mock_fastapi.set_post({"id": 3, "user_id": 3}, status=200)
        resp = admin_client.post(reverse("create_teacher"), {
            "username": "newteacher", "full_name": "Кузнецов К.К.",
            "email": "k@example.com", "password": "Teach123",
            "department": "ИТ", "position": "Преподаватель",
        })
        assert resp.status_code == 302


class TestOlympiadCreateFlow:
    """Администратор создаёт олимпиаду → POST в FastAPI."""

    def test_create_olympiad(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        mock_fastapi.set_post({"id": 5, "title": "Новая"}, status=200)
        resp = admin_client.post(reverse("create_olympiad"), {
            "title": "Новая олимпиада", "year": "2026", "level": "Городская",
        })
        assert resp.status_code == 302


class TestProtocolLifecycleFlow:
    """Жизненный цикл протокола: создать → подготовить → опубликовать."""

    def test_teacher_creates_protocol(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        mock_fastapi.set_post({"id": 1, "olympiad_id": 1, "status": "draft"}, status=200)
        resp = teacher_client.post(reverse("create_protocol"), {"olympiad_id": "1"})
        assert resp.status_code == 302

    def test_teacher_prepares_protocol(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        mock_fastapi.set_put({"id": 1, "status": "prepared"}, status=200)
        resp = teacher_client.post(reverse("set_protocol_prepared", args=[1]))
        assert resp.status_code == 302

    def test_teacher_recalls_protocol(self, teacher_client, mock_fastapi):
        mock_fastapi.set_role("teacher")
        mock_fastapi.set_put({"id": 1, "status": "draft"}, status=200)
        resp = teacher_client.post(reverse("recall_protocol", args=[1]))
        assert resp.status_code == 302

    def test_admin_publishes_protocol(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        mock_fastapi.set_put({"id": 1, "status": "published"}, status=200)
        resp = admin_client.post(reverse("publish_protocol", args=[1]))
        assert resp.status_code == 302


class TestReportFlow:
    """Годовой отчёт (CSV)."""

    def test_annual_report_csv(self, admin_client, mock_fastapi):
        mock_fastapi.set_role("admin")
        mock_fastapi.set_get_default([
            {"title": "Олимпиада А", "year": 2025, "level": "Рег.",
             "is_protocol_published": True},
        ])
        resp = admin_client.get(reverse("annual_report", args=[2025]))
        assert resp.status_code == 200
        assert "text/csv" in resp["Content-Type"]
        assert "attachment" in resp["Content-Disposition"]
