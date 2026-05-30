from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, StudentProfile, TeacherProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "role", "email", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительно", {"fields": ("role", "full_name")}),
    )


admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
