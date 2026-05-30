"""Контроллер преподавателей.

Бизнес-логика создания учётных записей преподавателей администратором.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.teacher import Teacher
from app.controllers import user as controller_user
from app.utils.security import get_password_hash
from app.schemas.user import TeacherCreate


def create_teacher(db: Session, teacher_data: TeacherCreate) -> Teacher:
    """Создание учётной записи преподавателя."""
    if controller_user.get_user_by_username(db, username=teacher_data.username):
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if controller_user.get_user_by_email(db, email=teacher_data.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    user = User(
        email=teacher_data.email,
        username=teacher_data.username,
        hashed_password=get_password_hash(teacher_data.password),
        full_name=teacher_data.full_name,
        role=UserRole.TEACHER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    teacher = Teacher(
        user_id=user.id,
        department=teacher_data.department,
        position=teacher_data.position,
        academic_degree=teacher_data.academic_degree,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
