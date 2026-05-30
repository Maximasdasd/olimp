from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),

    # Администратор — учетные записи преподавателей
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/create/", views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/edit/", views.teacher_edit, name="teacher_edit"),

    # Преподаватель — учетные записи студентов
    path("students/create/", views.student_create, name="student_create"),
]
