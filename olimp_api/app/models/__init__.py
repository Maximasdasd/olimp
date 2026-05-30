from .base import BaseModel
from .user import User, UserRole
from .student import Student
from .teacher import Teacher
from .olympiad import Olympiad
from .registration import Registration
from .protocol import Protocol, ProtocolResult
from .certificate import Certificate
from .task import Task

__all__ = [
    "BaseModel",
    "User", "UserRole",
    "Student",
    "Teacher", 
    "Olympiad",
    "Registration",
    "Protocol", "ProtocolResult",
    "Certificate",
    "Task"
]