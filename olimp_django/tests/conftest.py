"""
conftest.py — фикстуры для тестов Django-приложения «Олимпиадное движение».

В отличие от проекта AutoFleet (где Django проксирует запросы в FastAPI),
здесь Django — самостоятельное приложение со своей моделью пользователя,
ролями и входом по логину/паролю через стандартный механизм Django.

Поэтому используются обычные фикстуры:
  * пользователи создаются через User.objects.create_user;
  * вход выполняется через client.login(username, password);
  * фикстуры отдают готовые «залогиненные» клиенты для каждой роли
    (студент, преподаватель, администратор).
"""
import datetime

import pytest
from django.test import Client


# --- Ускорение тестов ----------------------------------------------------
# Быстрый хешер паролей вместо bcrypt — заметно ускоряет создание пользователей.
@pytest.fixture(autouse=True)
def _fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# --- ALLOWED_HOSTS -------------------------------------------------------
# Django test client ходит с хоста 'testserver'. Разрешаем его на время тестов.
@pytest.fixture(autouse=True)
def _allow_testserver(settings):
    settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]


# --- Клиенты -------------------------------------------------------------
@pytest.fixture
def client():
    """Анонимный Django test client (незарегистрированный пользователь)."""
    return Client()


# --- Пользователи по ролям ----------------------------------------------
@pytest.fixture
def admin_user(db):
    """Администратор."""
    from accounts.models import User
    return User.objects.create_user(
        username="admin", password="admin123",
        role=User.Role.ADMIN, full_name="Администратор Системы",
        email="admin@example.com", is_staff=True, is_superuser=True,
    )


@pytest.fixture
def teacher_user(db):
    """Преподаватель с профилем."""
    from accounts.models import User, TeacherProfile
    user = User.objects.create_user(
        username="teacher", password="teacher123",
        role=User.Role.TEACHER, full_name="Иванов Иван Иванович",
        email="teacher@example.com",
    )
    TeacherProfile.objects.create(user=user, department="Информатика", position="Доцент")
    return user


@pytest.fixture
def student_user(db):
    """Студент с профилем."""
    from accounts.models import User, StudentProfile
    user = User.objects.create_user(
        username="student", password="student123",
        role=User.Role.STUDENT, full_name="Петров Пётр Петрович",
        email="student@example.com",
    )
    StudentProfile.objects.create(
        user=user, institution="ЕМК", education_level="СПО",
        course=3, specialty="Информационные системы",
    )
    return user


@pytest.fixture
def admin_client(client, admin_user):
    """Клиент, залогиненный под администратором."""
    client.login(username="admin", password="admin123")
    return client


@pytest.fixture
def teacher_client(client, teacher_user):
    """Клиент, залогиненный под преподавателем."""
    client.login(username="teacher", password="teacher123")
    return client


@pytest.fixture
def student_client(client, student_user):
    """Клиент, залогиненный под студентом."""
    client.login(username="student", password="student123")
    return client


# --- Данные предметной области ------------------------------------------
@pytest.fixture
def olympiad(db, teacher_user):
    """Олимпиада с ответственным преподавателем."""
    from olympiads.models import Olympiad
    return Olympiad.objects.create(
        title="Олимпиада по программированию",
        description="Командная олимпиада по алгоритмам.",
        year=2025, level="Региональная",
        start_date=datetime.date(2025, 3, 1),
        end_date=datetime.date(2025, 3, 2),
        responsible_teacher=teacher_user,
    )


@pytest.fixture
def published_protocol(db, olympiad, teacher_user, student_user):
    """Опубликованный протокол с результатом студента."""
    from olympiads.models import Protocol, Result
    protocol = Protocol.objects.create(
        olympiad=olympiad, teacher=teacher_user,
        status=Protocol.Status.PUBLISHED,
    )
    Result.objects.create(
        protocol=protocol, student=student_user,
        score=95, place=1, result_type=Result.ResultType.WINNER,
    )
    return protocol


@pytest.fixture
def draft_protocol(db, olympiad, teacher_user):
    """Протокол в статусе «формируется»."""
    from olympiads.models import Protocol
    return Protocol.objects.create(
        olympiad=olympiad, teacher=teacher_user,
        status=Protocol.Status.DRAFT,
    )
