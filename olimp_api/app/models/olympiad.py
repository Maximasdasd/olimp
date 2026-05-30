from sqlalchemy import Column, String, Text, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Olympiad(BaseModel):
    __tablename__ = "olympiads"
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    registration_deadline = Column(Date, nullable=True) 
    location = Column(String(200))
    level = Column(String(50))  # Всероссийская, региональная, городская
    status = Column(String(20), default="planned")  # planned, ongoing, completed
    
    # Ответственный преподаватель
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    
    # Создатель (администратор)
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    # Файлы
    regulation_file = Column(String(500))
    tasks_file = Column(String(500))
    
    is_protocol_published = Column(Boolean, default=False)
    
    # Связи
    creator = relationship("User", back_populates="created_olympiads")
    responsible_teacher = relationship("Teacher", back_populates="olympiads")
    registrations = relationship("Registration", back_populates="olympiad")
    protocol = relationship("Protocol", back_populates="olympiad", uselist=False)
    certificates = relationship("Certificate", back_populates="olympiad")
    tasks = relationship("Task", back_populates="olympiad")
    
    def __repr__(self):
        return f"<Olympiad {self.title} ({self.year})>"