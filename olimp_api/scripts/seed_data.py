"""Наполнение БД PostgreSQL демонстрационными данными для FastAPI-бэкенда.

Запуск (из папки olimp_api):
    python -m scripts.seed_data

Создаёт администратора, преподавателя, студента, олимпиады и
опубликованный протокол с результатом.
"""
import datetime

from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.olympiad import Olympiad
from app.models.registration import Registration
from app.models.protocol import Protocol, ProtocolResult
from app.utils.security import get_password_hash


def get_or_create(db, model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    params = {**kwargs, **(defaults or {})}
    obj = model(**params)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj, True


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin, _ = get_or_create(
            db, User, username="admin",
            defaults=dict(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Администратор Системы",
                role=UserRole.ADMIN, is_active=True,
            ),
        )

        teacher_user, created = get_or_create(
            db, User, username="teacher",
            defaults=dict(
                email="teacher@example.com",
                hashed_password=get_password_hash("teacher123"),
                full_name="Иванов Иван Иванович",
                role=UserRole.TEACHER, is_active=True,
            ),
        )
        teacher, _ = get_or_create(
            db, Teacher, user_id=teacher_user.id,
            defaults=dict(department="Информатика", position="Доцент"),
        )

        student_user, _ = get_or_create(
            db, User, username="student",
            defaults=dict(
                email="student@example.com",
                hashed_password=get_password_hash("student123"),
                full_name="Петров Пётр Петрович",
                role=UserRole.STUDENT, is_active=True,
            ),
        )
        student, _ = get_or_create(
            db, Student, user_id=student_user.id,
            defaults=dict(
                institution="ЕМК", education_level="СПО",
                course=3, specialty="Информационные системы",
            ),
        )

        olymp1, _ = get_or_create(
            db, Olympiad, title="Олимпиада по программированию", year=2025,
            defaults=dict(
                description="Командная олимпиада по алгоритмам.",
                level="Региональная", creator_id=admin.id, teacher_id=teacher.id,
                start_date=datetime.date(2025, 3, 1),
                end_date=datetime.date(2025, 3, 2),
            ),
        )
        get_or_create(
            db, Olympiad, title="Конкурс веб-разработки", year=2024,
            defaults=dict(
                level="Городская", creator_id=admin.id, teacher_id=teacher.id,
                start_date=datetime.date(2024, 4, 10),
                end_date=datetime.date(2024, 4, 11),
            ),
        )

        get_or_create(db, Registration, olympiad_id=olymp1.id, student_id=student.id,
                      defaults=dict(status="registered"))

        protocol, created = get_or_create(
            db, Protocol, olympiad_id=olymp1.id,
            defaults=dict(teacher_id=teacher.id, status="published"),
        )
        if created:
            olymp1.is_protocol_published = True
            db.add(ProtocolResult(
                protocol_id=protocol.id, student_id=student.id,
                score=95, place=1, result_type="winner",
            ))
            db.commit()

        print("Демо-данные созданы в PostgreSQL:")
        print("  admin / admin123 (администратор)")
        print("  teacher / teacher123 (преподаватель)")
        print("  student / student123 (студент)")
    finally:
        db.close()


if __name__ == "__main__":
    run()
