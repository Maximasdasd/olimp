from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Protocol(BaseModel):
    __tablename__ = "protocols"
    
    olympiad_id = Column(Integer, ForeignKey("olympiads.id"), unique=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    status = Column(String(20), default="draft")  # draft, prepared, published
    file_path = Column(String(500))
    
    # Связи
    olympiad = relationship("Olympiad", back_populates="protocol")
    teacher = relationship("Teacher", back_populates="created_protocols")
    results = relationship("ProtocolResult", back_populates="protocol")
    
    def __repr__(self):
        return f"<Protocol for {self.olympiad.title}>"

class ProtocolResult(BaseModel):
    __tablename__ = "protocol_results"
    
    protocol_id = Column(Integer, ForeignKey("protocols.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    score = Column(Float)
    place = Column(Integer)
    result_type = Column(String(20))  # winner, prize_winner, participant
    certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=True)
    
    # Связи
    protocol = relationship("Protocol", back_populates="results")
    student = relationship("Student", back_populates="results")
    certificate = relationship("Certificate", back_populates="result")
    
    def __repr__(self):
        return f"<Result {self.student_id}: {self.score} points>"