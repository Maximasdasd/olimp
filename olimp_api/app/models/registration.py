from sqlalchemy import Column, Integer, ForeignKey, DateTime, String  
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel

class Registration(BaseModel):
    __tablename__ = "registrations"
    
    olympiad_id = Column(Integer, ForeignKey("olympiads.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="registered")  # registered, confirmed, cancelled
    
    # Связи
    olympiad = relationship("Olympiad", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")
    
    def __repr__(self):
        return f"<Registration {self.student_id} -> {self.olympiad_id}>"