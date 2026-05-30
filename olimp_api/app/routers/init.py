from .auth import router as auth_router
from .public import router as public_router
from .student import router as student_router
from .teacher import router as teacher_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "public_router", 
    "student_router",
    "teacher_router",
    "admin_router"
]