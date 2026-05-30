from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Certificate(BaseModel):
    __tablename__ = "certificates"
    
    olympiad_id = Column(Integer, ForeignKey("olympiads.id"))
    certificate_type = Column(String(50))  # грамота, сертификат, диплом
    template_file = Column(String(500))
    
    # Связи
    olympiad = relationship("Olympiad", back_populates="certificates")
    result = relationship("ProtocolResult", back_populates="certificate")
    
    def __repr__(self):
        return f"<Certificate {self.certificate_type} for {self.olympiad.title}>"