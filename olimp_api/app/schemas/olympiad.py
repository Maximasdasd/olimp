from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class OlympiadBase(BaseModel):
    title: str
    description: Optional[str] = None
    year: int
    start_date: date
    end_date: date
    registration_deadline: Optional[date] = None
    location: Optional[str] = None
    level: str
    status: str = "planned"

class OlympiadCreate(OlympiadBase):
    teacher_id: int

class OlympiadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_deadline: Optional[date] = None
    location: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = None
    teacher_id: Optional[int] = None

class OlympiadResponse(OlympiadBase):
    id: int
    teacher_id: Optional[int]
    creator_id: Optional[int]
    is_protocol_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Для публичного доступа (без чувствительных данных)
class OlympiadPublic(BaseModel):
    id: int
    title: str
    description: Optional[str]
    year: int
    start_date: date
    end_date: date
    location: Optional[str]
    level: str
    status: str
    
    class Config:
        from_attributes = True

class RegistrationBase(BaseModel):
    olympiad_id: int
    student_id: int

class RegistrationResponse(RegistrationBase):
    id: int
    registration_date: datetime
    status: str
    
    class Config:
        from_attributes = True