from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Teacher(BaseModel):
    __tablename__ = "teachers"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department = Column(String(100))
    position = Column(String(100))
    academic_degree = Column(String(50))
    
    # Связи
    user = relationship("User", back_populates="teacher_profile")
    olympiads = relationship("Olympiad", back_populates="responsible_teacher")
    created_protocols = relationship("Protocol", back_populates="teacher")
    
    def __repr__(self):
        return f"<Teacher {self.user.full_name if self.user else 'No user'}>"