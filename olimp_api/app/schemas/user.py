from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from app.models.user import UserRole


# ---------- Пользователь ----------
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Ответ при входе/регистрации с access-токеном."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


# ---------- Студент ----------
class StudentCreate(BaseModel):
    """Создание учетной записи студента (преподавателем)."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    institution: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[int] = None
    specialty: Optional[str] = None


class StudentProfileUpdate(BaseModel):
    """Редактирование профиля студента."""
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    institution: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[int] = None
    specialty: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    institution: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[int] = None
    specialty: Optional[str] = None

    class Config:
        from_attributes = True


class StudentResponseFull(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    username: str
    email: EmailStr


# ---------- Преподаватель ----------
class TeacherCreate(BaseModel):
    """Создание учетной записи преподавателя (администратором)."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    academic_degree: Optional[str] = None


class TeacherResponse(BaseModel):
    id: int
    user_id: int
    department: Optional[str] = None
    position: Optional[str] = None
    academic_degree: Optional[str] = None

    class Config:
        from_attributes = True
