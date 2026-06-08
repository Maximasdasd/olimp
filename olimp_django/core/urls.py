from django.urls import path

from . import views

urlpatterns = [
    # Аутентификация
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Публичное
    path("", views.olympiad_list, name="olympiad_list"),
    path("olympiad/<int:pk>/", views.olympiad_detail, name="olympiad_detail"),

    # Студент
    path("olympiad/<int:pk>/register/", views.register_for_olympiad, name="register_for_olympiad"),
    path("profile/", views.my_profile, name="profile"),

    # Преподаватель
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/students/create/", views.create_student, name="create_student"),
    path("teacher/protocol/create/", views.create_protocol, name="create_protocol"),
    path("teacher/protocol/<int:protocol_id>/results/", views.add_result, name="add_result"),
    path("teacher/protocol/<int:protocol_id>/prepared/", views.set_protocol_prepared, name="set_protocol_prepared"),
    path("teacher/protocol/<int:protocol_id>/recall/", views.recall_protocol, name="recall_protocol"),

    # Администратор
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/olympiad/create/", views.create_olympiad, name="create_olympiad"),
    path("manage/teacher/create/", views.create_teacher, name="create_teacher"),
    path("manage/protocol/<int:protocol_id>/publish/", views.publish_protocol, name="publish_protocol"),

    # Отчёты
    path("report/annual/<int:year>/", views.annual_report, name="annual_report"),
]
