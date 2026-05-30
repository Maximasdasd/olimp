import pytest
from datetime import date
from app.models import User, Student, Teacher, Olympiad, UserRole

def test_user_model():
    """Тест модели пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Тестовый Пользователь",
        role=UserRole.STUDENT
    )
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.STUDENT
    assert user.is_active == True

def test_student_model():
    """Тест модели студента"""
    student = Student(
        birth_date=date(2000, 1, 1),
        institution="Университет",
        education_level="Бакалавриат",
        course=3,
        specialty="Программирование"
    )
    
    assert student.course == 3
    assert student.institution == "Университет"

def test_olympiad_model():
    """Тест модели олимпиады"""
    olympiad = Olympiad(
        title="Тестовая олимпиада",
        year=2024,
        start_date=date(2024, 12, 20),
        end_date=date(2024, 12, 21),
        level="Региональная",
        status="planned"
    )
    
    assert olympiad.title == "Тестовая олимпиада"
    assert olympiad.year == 2024
    assert olympiad.is_protocol_published == False