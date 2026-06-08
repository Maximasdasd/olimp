"""Контекст-процессоры: данные, доступные во всех шаблонах."""
from .fastapi_client import get_current_user


def current_user(request):
    """Добавляет текущего пользователя FastAPI в контекст шаблонов."""
    user = get_current_user(request)
    role = user.get("role") if user else None
    return {
        "current_user": user,
        "is_authenticated": user is not None,
        "is_admin": role == "admin",
        "is_teacher": role in ("teacher", "admin"),
        "is_student": role == "student",
    }
