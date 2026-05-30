from pydantic import BaseModel
from typing import Optional


class ProtocolCreate(BaseModel):
    olympiad_id: int


class ProtocolResponse(BaseModel):
    id: int
    olympiad_id: int
    teacher_id: Optional[int] = None
    status: str
    file_path: Optional[str] = None

    class Config:
        from_attributes = True


class ProtocolStatusUpdate(BaseModel):
    # Допустимые статусы: draft (формируется), prepared (подготовлен), published (опубликован)
    status: str


class ProtocolResultCreate(BaseModel):
    student_id: int
    score: float
    place: Optional[int] = None
    # Тип результата: winner (победитель), prize_winner (призер), participant (участник)
    result_type: str


class ProtocolResultResponse(BaseModel):
    id: int
    protocol_id: int
    student_id: int
    score: Optional[float] = None
    place: Optional[int] = None
    result_type: Optional[str] = None

    class Config:
        from_attributes = True
