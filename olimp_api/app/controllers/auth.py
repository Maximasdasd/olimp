"""Контроллер аутентификации.

Содержит бизнес-логику регистрации, проверки учётных данных
и формирования ответа с JWT-токеном. Роутер (View) только вызывает
эти функции и не работает с БД напрямую.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.controllers import user as controller_user
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.security import verify_password, create_access_token


def register_user(db: Session, user_data: UserCreate) -> User:
    """Регистрация нового пользователя с проверкой уникальности."""
    if controller_user.get_user_by_username(db, username=user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )
    if controller_user.get_user_by_email(db, email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    return controller_user.create_user(db, user_data)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Проверка логина и пароля. Возвращает пользователя или None."""
    user = controller_user.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def build_token_response(user: User) -> dict:
    """Формирование ответа с access-токеном для пользователя."""
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value,
    }
