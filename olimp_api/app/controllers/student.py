"""Контроллер студентов.

Бизнес-логика профиля студента, записи на олимпиады,
просмотра результатов и создания учётных записей студентов.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.models.student import Student
from app.models.registration import Registration
from app.models.olympiad import Olympiad
from app.models.protocol import ProtocolResult
from app.controllers import user as controller_user
from app.utils.security import get_password_hash
from app.schemas.user import StudentCreate, StudentProfileUpdate, StudentResponseFull


def get_student_by_user(db: Session, user_id: int) -> Student:
    """Профиль студента по id пользователя или 404."""
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Профиль студента не найден")
    return student


def register_for_olympiad(db: Session, user_id: int, olympiad_id: int) -> Registration:
    """Запись студента на олимпиаду."""
    student = get_student_by_user(db, user_id)

    olympiad = db.query(Olympiad).filter(Olympiad.id == olympiad_id).first()
    if not olympiad:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")

    existing = db.query(Registration).filter(
        Registration.student_id == student.id,
        Registration.olympiad_id == olympiad_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже записаны на эту олимпиаду")

    registration = Registration(
        student_id=student.id,
        olympiad_id=olympiad_id,
        status="registered",
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def get_my_olympiads(db: Session, user_id: int):
    """Список олимпиад, на которые записан студент."""
    student = get_student_by_user(db, user_id)
    return db.query(Registration).filter(Registration.student_id == student.id).all()


def get_my_results(db: Session, user_id: int):
    """Результаты участия студента."""
    student = get_student_by_user(db, user_id)
    return db.query(ProtocolResult).filter(ProtocolResult.student_id == student.id).all()


def update_profile(db: Session, user_id: int, profile_data: StudentProfileUpdate) -> Student:
    """Редактирование профиля студента."""
    student = get_student_by_user(db, user_id)
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def create_student(db: Session, student_data: StudentCreate) -> StudentResponseFull:
    """Создание учётной записи студента преподавателем."""
    if controller_user.get_user_by_username(db, username=student_data.username):
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if controller_user.get_user_by_email(db, email=student_data.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    user = User(
        email=student_data.email,
        username=student_data.username,
        hashed_password=get_password_hash(student_data.password),
        full_name=student_data.full_name,
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    student = Student(
        user_id=user.id,
        birth_date=student_data.birth_date,
        phone=student_data.phone,
        institution=student_data.institution,
        education_level=student_data.education_level,
        course=student_data.course,
        specialty=student_data.specialty,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentResponseFull(
        id=student.id,
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
    )
