from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from app.models.user import UserRole

# Базовые схемы
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

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для студентов
class StudentBase(BaseModel):
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    institution: str
    education_level: str
    course: int
    specialty: str

class StudentCreate(StudentBase):
    user: UserCreate

class StudentResponse(StudentBase):
    id: int
    user: UserInDB
    
    class Config:
        from_attributes = True

# Схемы для преподавателей
class TeacherBase(BaseModel):
    department: str
    position: str
    academic_degree: Optional[str] = None

class TeacherCreate(TeacherBase):
    user: UserCreate

class TeacherResponse(TeacherBase):
    id: int
    user: UserInDB
    
    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole
    # Поля для студента (если role == STUDENT)
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    institution: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[int] = None
    specialty: Optional[str] = None
    # Поля для преподавателя (если role == TEACHER)
    department: Optional[str] = None
    position: Optional[str] = None
    academic_degree: Optional[str] = None

    
class UserLogin(BaseModel):
    username: str
    password: str