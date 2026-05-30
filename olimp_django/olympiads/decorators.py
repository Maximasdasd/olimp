"""Декораторы проверки ролей для веб-представлений."""
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """Доступ только пользователям с указанными ролями (админ проходит всегда)."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_admin or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Недостаточно прав для этого действия.")
        return _wrapped
    return decorator


admin_required = role_required("admin")
teacher_required = role_required("teacher")
student_required = role_required("student")
