from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = "tasks"
    
    olympiad_id = Column(Integer, ForeignKey("olympiads.id"))
    year = Column(Integer)
    task_text = Column(Text)
    solution = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    
    # Связи
    olympiad = relationship("Olympiad", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.year} for {self.olympiad.title}>"