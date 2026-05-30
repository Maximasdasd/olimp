from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class OlympiadBase(BaseModel):
    title: str
    description: Optional[str] = None
    year: int
    start_date: date
    end_date: date
    registration_deadline: Optional[date] = None
    location: Optional[str] = None
    level: Optional[str] = None
    status: str = "planned"


class OlympiadCreate(OlympiadBase):
    teacher_id: Optional[int] = None


class OlympiadResponse(OlympiadBase):
    id: int
    teacher_id: Optional[int] = None
    creator_id: Optional[int] = None
    is_protocol_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    id: int
    olympiad_id: int
    student_id: int
    registration_date: datetime
    status: str

    class Config:
        from_attributes = True
