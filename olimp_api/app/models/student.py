from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

from app.models.base import BaseModel

class Student(BaseModel):
    __tablename__ = "students"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    birth_date = Column(Date)
    phone = Column(String(20))
    institution = Column(String(200))
    education_level = Column(String(50))  # Бакалавриат, магистратура 
    course = Column(Integer)
    specialty = Column(String(100))
    
    # Связи
    user = relationship("User", back_populates="student_profile")
    registrations = relationship("Registration", back_populates="student")
    results = relationship("ProtocolResult", back_populates="student")
    
    def __repr__(self):
        return f"<Student {self.user.full_name if self.user else 'No user'}>"