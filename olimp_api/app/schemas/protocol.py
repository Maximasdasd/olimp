from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProtocolBase(BaseModel):
    olympiad_id: int
    status: str = "draft"  # draft, prepared, published

class ProtocolCreate(ProtocolBase):
    teacher_id: int

class ProtocolUpdate(BaseModel):
    status: Optional[str] = None
    file_path: Optional[str] = None

class ProtocolResponse(ProtocolBase):
    id: int
    teacher_id: Optional[int]
    file_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProtocolResultBase(BaseModel):
    student_id: int
    score: float
    place: Optional[int] = None
    result_type: str  # winner, prize_winner, participant

class ProtocolResultResponse(ProtocolResultBase):
    id: int
    protocol_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True