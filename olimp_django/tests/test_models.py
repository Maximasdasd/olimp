"""
Тесты моделей и доменной логики приложения «Олимпиадное движение».

В проекте AutoFleet здесь тестировался клиент к FastAPI (core/fastapi_client).
В olimp_django Django самодостаточен, поэтому на этом уровне проверяется
собственная доменная логика: модель пользователя с ролями, профили,
свойства олимпиады и протокола.
"""
import pytest

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────
#  Пользователь и роли
# ──────────────────────────────────────────────
class TestUserRoles:
    def test_admin_flags(self, admin_user):
        assert admin_user.is_admin is True
        assert admin_user.is_teacher is False
        assert admin_user.is_student is False

    def test_teacher_flags(self, teacher_user):
        assert teacher_user.is_teacher is True
        assert teacher_user.is_admin is False

    def test_student_flags(self, student_user):
        assert student_user.is_student is True
        assert student_user.is_teacher is False

    def test_role_choices_values(self):
        from accounts.models import User
        assert User.Role.ADMIN == "admin"
        assert User.Role.TEACHER == "teacher"
        assert User.Role.STUDENT == "student"

    def test_display_name_prefers_full_name(self, student_user):
        assert student_user.display_name() == "Петров Пётр Петрович"

    def test_display_name_falls_back_to_username(self, db):
        from accounts.models import User
        user = User.objects.create_user(username="nameless", password="x")
        assert user.display_name() == "nameless"

    def test_superuser_is_admin_even_without_role(self, db):
        from accounts.models import User
        user = User.objects.create_user(
            username="root", password="x",
            role=User.Role.STUDENT, is_superuser=True,
        )
        # суперпользователь считается администратором
        assert user.is_admin is True


# ──────────────────────────────────────────────
#  Профили
# ──────────────────────────────────────────────
class TestProfiles:
    def test_student_profile_linked(self, student_user):
        assert student_user.student_profile.institution == "ЕМК"
        assert student_user.student_profile.course == 3

    def test_teacher_profile_linked(self, teacher_user):
        assert teacher_user.teacher_profile.department == "Информатика"

    def test_student_profile_str(self, student_user):
        assert "Петров" in str(student_user.student_profile)


# ──────────────────────────────────────────────
#  Олимпиада
# ──────────────────────────────────────────────
class TestOlympiad:
    def test_str(self, olympiad):
        assert str(olympiad) == "Олимпиада по программированию (2025)"

    def test_no_published_protocol_by_default(self, olympiad):
        assert olympiad.has_published_protocol is False
        assert olympiad.published_protocol is None

    def test_has_published_protocol(self, olympiad, published_protocol):
        assert olympiad.has_published_protocol is True
        assert olympiad.published_protocol == published_protocol

    def test_draft_protocol_not_counted_as_published(self, olympiad, draft_protocol):
        assert olympiad.has_published_protocol is False


# ──────────────────────────────────────────────
#  Протокол и результаты
# ──────────────────────────────────────────────
class TestProtocol:
    def test_default_status_is_draft(self, draft_protocol):
        from olympiads.models import Protocol
        assert draft_protocol.status == Protocol.Status.DRAFT

    def test_status_display(self, draft_protocol):
        assert draft_protocol.get_status_display() == "Формируется"

    def test_result_belongs_to_protocol(self, published_protocol):
        result = published_protocol.results.first()
        assert result.score == 95
        assert result.place == 1

    def test_result_type_display(self, published_protocol):
        result = published_protocol.results.first()
        assert result.get_result_type_display() == "Победитель"


# ──────────────────────────────────────────────
#  Запись на олимпиаду
# ──────────────────────────────────────────────
class TestRegistration:
    def test_unique_together(self, db, olympiad, student_user):
        from django.db import IntegrityError
        from olympiads.models import Registration
        Registration.objects.create(olympiad=olympiad, student=student_user)
        # повторная запись того же студента на ту же олимпиаду запрещена на уровне БД
        with pytest.raises(IntegrityError):
            Registration.objects.create(olympiad=olympiad, student=student_user)


# ──────────────────────────────────────────────
#  Сертификаты/грамоты
# ──────────────────────────────────────────────
class TestCertificate:
    def test_multiple_certificates_per_olympiad(self, db, olympiad):
        # к одной олимпиаде можно добавить любое количество бланков (по ТЗ)
        from olympiads.models import Certificate
        Certificate.objects.create(olympiad=olympiad, title="Грамота за 1 место",
                                    cert_type=Certificate.CertType.DIPLOMA)
        Certificate.objects.create(olympiad=olympiad, title="Сертификат участника",
                                   cert_type=Certificate.CertType.CERTIFICATE)
        assert olympiad.certificates.count() == 2
