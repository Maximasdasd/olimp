"""
Тесты Django-вьюх приложения «Олимпиадное движение».

Покрывают:
  * публичные страницы (список олимпиад, карточка) — доступны всем;
  * редиректы на логин для защищённых страниц без входа;
  * проверку прав по ролям (студент/преподаватель/администратор);
  * успешный рендер страниц и проверку заголовков;
  * процессы входа, регистрации и выхода.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db  # сессии и данные используют БД


# ──────────────────────────────────────────────
#  Публичные страницы (незарегистрированный пользователь)
# ──────────────────────────────────────────────
class TestPublicPages:
    def test_olympiad_list_ok(self, client):
        response = client.get(reverse("olympiad_list"))
        assert response.status_code == 200

    def test_olympiad_list_title(self, client):
        response = client.get(reverse("olympiad_list"))
        assert "Олимпиады" in response.content.decode("utf-8")

    def test_olympiad_list_shows_olympiad(self, client, olympiad):
        response = client.get(reverse("olympiad_list"))
        assert olympiad.title in response.content.decode("utf-8")

    def test_olympiad_list_filter_by_year(self, client, olympiad):
        # фильтр по году, на который есть олимпиада
        response = client.get(reverse("olympiad_list"), {"year": 2025})
        assert response.status_code == 200
        assert olympiad.title in response.content.decode("utf-8")

    def test_olympiad_list_filter_other_year_hides(self, client, olympiad):
        # год без олимпиад — карточки нет
        response = client.get(reverse("olympiad_list"), {"year": 1999})
        assert olympiad.title not in response.content.decode("utf-8")

    def test_olympiad_detail_ok(self, client, olympiad):
        response = client.get(reverse("olympiad_detail", args=[olympiad.pk]))
        assert response.status_code == 200
        assert olympiad.title in response.content.decode("utf-8")

    def test_olympiad_detail_404(self, client):
        response = client.get(reverse("olympiad_detail", args=[999999]))
        assert response.status_code == 404

    def test_published_protocol_visible_to_anon(self, client, olympiad, published_protocol):
        # опубликованный протокол виден незарегистрированному пользователю
        response = client.get(reverse("olympiad_detail", args=[olympiad.pk]))
        content = response.content.decode("utf-8")
        assert "Победитель" in content


# ──────────────────────────────────────────────
#  Доступ без входа → редирект на логин
# ──────────────────────────────────────────────
class TestAuthRedirects:
    @pytest.mark.parametrize("route", [
        "profile", "teacher_dashboard", "admin_dashboard",
        "create_protocol", "olympiad_create", "teacher_list",
        "teacher_create", "student_create",
    ])
    def test_protected_pages_redirect_to_login(self, client, route):
        response = client.get(reverse(route))
        assert response.status_code == 302
        assert reverse("login") in response.url


# ──────────────────────────────────────────────
#  Контроль доступа по ролям
# ──────────────────────────────────────────────
class TestRolePermissions:
    def test_student_cannot_open_admin(self, student_client):
        # студенту запрещена админ-панель → 403
        response = student_client.get(reverse("admin_dashboard"))
        assert response.status_code == 403

    def test_student_cannot_open_teacher(self, student_client):
        response = student_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 403

    def test_teacher_cannot_open_admin(self, teacher_client):
        response = teacher_client.get(reverse("admin_dashboard"))
        assert response.status_code == 403

    def test_admin_can_open_teacher_pages(self, admin_client):
        # администратор проходит проверку преподавателя (по реализации декоратора)
        response = admin_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Студент
# ──────────────────────────────────────────────
class TestStudentPages:
    def test_profile_ok(self, student_client):
        response = student_client.get(reverse("profile"))
        assert response.status_code == 200

    def test_profile_title(self, student_client):
        response = student_client.get(reverse("profile"))
        assert "Мой профиль" in response.content.decode("utf-8")


# ──────────────────────────────────────────────
#  Преподаватель
# ──────────────────────────────────────────────
class TestTeacherPages:
    def test_dashboard_ok(self, teacher_client):
        response = teacher_client.get(reverse("teacher_dashboard"))
        assert response.status_code == 200

    def test_dashboard_title(self, teacher_client):
        response = teacher_client.get(reverse("teacher_dashboard"))
        assert "Кабинет преподавателя" in response.content.decode("utf-8")

    def test_student_create_form_ok(self, teacher_client):
        response = teacher_client.get(reverse("student_create"))
        assert response.status_code == 200
        assert "Создание студента" in response.content.decode("utf-8")

    def test_create_protocol_form_ok(self, teacher_client):
        response = teacher_client.get(reverse("create_protocol"))
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Администратор
# ──────────────────────────────────────────────
class TestAdminPages:
    def test_dashboard_ok(self, admin_client):
        response = admin_client.get(reverse("admin_dashboard"))
        assert response.status_code == 200

    def test_dashboard_title(self, admin_client):
        response = admin_client.get(reverse("admin_dashboard"))
        assert "Панель администратора" in response.content.decode("utf-8")

    def test_olympiad_create_form_ok(self, admin_client):
        response = admin_client.get(reverse("olympiad_create"))
        assert response.status_code == 200

    def test_teacher_list_ok(self, admin_client, teacher_user):
        response = admin_client.get(reverse("teacher_list"))
        assert response.status_code == 200
        assert teacher_user.display_name() in response.content.decode("utf-8")

    def test_teacher_create_form_ok(self, admin_client):
        response = admin_client.get(reverse("teacher_create"))
        assert response.status_code == 200
        assert "Создание преподавателя" in response.content.decode("utf-8")


# ──────────────────────────────────────────────
#  Вход / регистрация / выход
# ──────────────────────────────────────────────
class TestLogin:
    def test_login_page_ok(self, client):
        response = client.get(reverse("login"))
        assert response.status_code == 200
        assert "Вход" in response.content.decode("utf-8")

    def test_login_success_redirects(self, client, student_user):
        response = client.post(reverse("login"), {
            "username": "student", "password": "student123",
        })
        assert response.status_code == 302
        # после входа пользователь аутентифицирован
        assert response.wsgi_request.user.is_authenticated

    def test_login_wrong_password(self, client, student_user):
        response = client.post(reverse("login"), {
            "username": "student", "password": "wrong",
        })
        # форма перерисовывается со статусом 200, вход не выполнен
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated


class TestRegister:
    def test_register_page_ok(self, client):
        response = client.get(reverse("register"))
        assert response.status_code == 200
        assert "Регистрация" in response.content.decode("utf-8")

    def test_register_creates_student(self, client):
        from accounts.models import User
        response = client.post(reverse("register"), {
            "username": "newstudent",
            "full_name": "Новиков Новик Новикович",
            "email": "new@example.com",
            "password1": "SuperPass123",
            "password2": "SuperPass123",
        })
        assert response.status_code == 302
        user = User.objects.get(username="newstudent")
        assert user.role == User.Role.STUDENT
        # автоматически создан профиль студента
        assert hasattr(user, "student_profile")


class TestLogout:
    def test_logout_redirects(self, student_client):
        response = student_client.post(reverse("logout"))
        assert response.status_code == 302
