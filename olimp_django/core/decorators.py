"""Декораторы доступа на основе роли пользователя из FastAPI."""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .fastapi_client import get_current_user


def login_required(view_func):
    """Требует входа (наличие токена FastAPI). Иначе редирект на /login/."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not get_current_user(request):
            return redirect(f"/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped


def role_required(*roles):
    """Доступ только указанным ролям (админ проходит всегда)."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                return redirect(f"/login/?next={request.path}")
            role = user.get("role")
            if role == "admin" or role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Недостаточно прав для этого действия.")
            return redirect("olympiad_list")
        return _wrapped
    return decorator


admin_required = role_required("admin")
teacher_required = role_required("teacher")
student_required = role_required("student")
