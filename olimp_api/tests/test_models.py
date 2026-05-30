from app.models import User, UserRole, Olympiad, Protocol


def test_user_model():
    user = User(
        email="m@example.com",
        username="m",
        hashed_password="x",
        full_name="М",
        role=UserRole.ADMIN,
    )
    assert user.username == "m"
    assert user.role == UserRole.ADMIN


def test_user_roles():
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.TEACHER.value == "teacher"
    assert UserRole.STUDENT.value == "student"


def test_olympiad_model():
    olympiad = Olympiad(title="Тест", year=2025)
    assert olympiad.title == "Тест"
    assert olympiad.year == 2025


def test_protocol_default_status():
    protocol = Protocol(olympiad_id=1, teacher_id=1, status="draft")
    assert protocol.status == "draft"
