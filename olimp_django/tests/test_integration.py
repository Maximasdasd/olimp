"""
Интеграционные тесты пользовательских сценариев Django-приложения.

Проверяют сквозные сценарии в рамках Django-слоя:
вход → доступ к странице, отправка формы → изменение данных в БД,
полный жизненный цикл протокола (формируется → подготовлен → опубликован).
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestLoginFlow:
    """Сценарий входа и последующего доступа к защищённым страницам."""

    def test_login_then_profile(self, client, student_user):
        # 1. логинимся
        client.post(reverse("login"), {
            "username": "student", "password": "student123",
        })
        # 2. теперь личный кабинет доступен (200), а не редирект
        resp = client.get(reverse("profile"))
        assert resp.status_code == 200

    def test_no_login_no_access(self, client):
        """Без входа защищённая страница ведёт на логин."""
        resp = client.get(reverse("profile"))
        assert resp.status_code == 302
        assert reverse("login") in resp.url


class TestStudentRegistrationFlow:
    """Самостоятельная регистрация студента и вход в кабинет."""

    def test_register_then_dashboard(self, client):
        from accounts.models import User
        resp = client.post(reverse("register"), {
            "username": "ivanov", "full_name": "Иванов И.И.",
            "email": "ivanov@example.com",
            "password1": "Pass123word", "password2": "Pass123word",
        })
        assert resp.status_code == 302
        # после регистрации пользователь уже залогинен
        assert User.objects.filter(username="ivanov").exists()
        profile = client.get(reverse("profile"))
        assert profile.status_code == 200


class TestOlympiadRegistrationFlow:
    """Запись студента на олимпиаду через форму."""

    def test_student_registers_for_olympiad(self, student_client, olympiad, student_user):
        from olympiads.models import Registration
        resp = student_client.post(reverse("register_for_olympiad", args=[olympiad.pk]))
        assert resp.status_code == 302
        assert Registration.objects.filter(
            olympiad=olympiad, student=student_user
        ).exists()

    def test_double_registration_no_duplicate(self, student_client, olympiad, student_user):
        from olympiads.models import Registration
        student_client.post(reverse("register_for_olympiad", args=[olympiad.pk]))
        student_client.post(reverse("register_for_olympiad", args=[olympiad.pk]))
        # повторная запись не создаёт дубликат
        assert Registration.objects.filter(
            olympiad=olympiad, student=student_user
        ).count() == 1


class TestTeacherCreatesStudentFlow:
    """Преподаватель создаёт учётную запись студента."""

    def test_create_student_account(self, teacher_client):
        from accounts.models import User
        resp = teacher_client.post(reverse("student_create"), {
            "username": "newpupil", "full_name": "Сидоров С.С.",
            "email": "pupil@example.com",
            "password1": "Pupil123pass", "password2": "Pupil123pass",
            "institution": "ЕМК", "education_level": "СПО",
            "course": 2, "specialty": "ИП",
        })
        assert resp.status_code == 302
        user = User.objects.get(username="newpupil")
        assert user.role == User.Role.STUDENT
        assert hasattr(user, "student_profile")


class TestAdminCreatesTeacherFlow:
    """Администратор создаёт учётную запись преподавателя."""

    def test_create_teacher_account(self, admin_client):
        from accounts.models import User
        resp = admin_client.post(reverse("teacher_create"), {
            "username": "newteacher", "full_name": "Кузнецов К.К.",
            "email": "kuz@example.com",
            "password1": "Teach123pass", "password2": "Teach123pass",
            "department": "Математика", "position": "Преподаватель",
        })
        assert resp.status_code == 302
        user = User.objects.get(username="newteacher")
        assert user.role == User.Role.TEACHER
        assert hasattr(user, "teacher_profile")


class TestOlympiadCreateFlow:
    """Администратор заполняет карточку олимпиады."""

    def test_admin_creates_olympiad(self, admin_client, teacher_user):
        from olympiads.models import Olympiad
        resp = admin_client.post(reverse("olympiad_create"), {
            "title": "Новая олимпиада", "description": "Описание",
            "year": 2026, "level": "Городская",
            "responsible_teacher": teacher_user.pk,
        })
        assert resp.status_code == 302
        assert Olympiad.objects.filter(title="Новая олимпиада").exists()


class TestProtocolLifecycleFlow:
    """
    Полный жизненный цикл протокола по ТЗ:
    формируется → подготовлен → опубликован, плюс отзыв подготовленного.
    """

    def test_full_protocol_lifecycle(self, teacher_client, admin_client, draft_protocol):
        from olympiads.models import Protocol

        # 1. преподаватель добавляет результат
        from accounts.models import User, StudentProfile
        pupil = User.objects.create_user(
            username="pupil2", password="x", role=User.Role.STUDENT,
            full_name="Ученик Второй",
        )
        StudentProfile.objects.create(user=pupil)
        teacher_client.post(reverse("protocol_edit", args=[draft_protocol.pk]), {
            "student": pupil.pk, "score": 80, "place": 2,
            "result_type": "prize_winner",
        })
        assert draft_protocol.results.count() == 1

        # 2. преподаватель переводит в «подготовлен»
        teacher_client.post(reverse("protocol_set_prepared", args=[draft_protocol.pk]))
        draft_protocol.refresh_from_db()
        assert draft_protocol.status == Protocol.Status.PREPARED

        # 3. администратор публикует
        admin_client.post(reverse("protocol_publish", args=[draft_protocol.pk]))
        draft_protocol.refresh_from_db()
        assert draft_protocol.status == Protocol.Status.PUBLISHED

    def test_recall_only_prepared(self, teacher_client, draft_protocol):
        from olympiads.models import Protocol
        # черновик отозвать нельзя — статус не меняется
        teacher_client.post(reverse("protocol_recall", args=[draft_protocol.pk]))
        draft_protocol.refresh_from_db()
        assert draft_protocol.status == Protocol.Status.DRAFT

        # подготовленный — можно вернуть в черновик
        draft_protocol.status = Protocol.Status.PREPARED
        draft_protocol.save()
        teacher_client.post(reverse("protocol_recall", args=[draft_protocol.pk]))
        draft_protocol.refresh_from_db()
        assert draft_protocol.status == Protocol.Status.DRAFT

    def test_publish_requires_prepared(self, admin_client, draft_protocol):
        from olympiads.models import Protocol
        # опубликовать можно только подготовленный — черновик не публикуется
        admin_client.post(reverse("protocol_publish", args=[draft_protocol.pk]))
        draft_protocol.refresh_from_db()
        assert draft_protocol.status == Protocol.Status.DRAFT


class TestReportFlow:
    """Формирование отчётов (CSV/Excel)."""

    def test_protocol_report_csv(self, teacher_client, published_protocol):
        resp = teacher_client.get(reverse("report_protocol", args=[published_protocol.pk]))
        assert resp.status_code == 200
        assert "text/csv" in resp["Content-Type"]
        assert "attachment" in resp["Content-Disposition"]

    def test_annual_report_csv(self, admin_client, published_protocol):
        resp = admin_client.get(reverse("report_annual", args=[2025]))
        assert resp.status_code == 200
        assert "text/csv" in resp["Content-Type"]
