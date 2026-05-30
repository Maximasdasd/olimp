from django.urls import path

from . import views

urlpatterns = [
    # Публичное
    path("", views.olympiad_list, name="olympiad_list"),
    path("olympiad/<int:pk>/", views.olympiad_detail, name="olympiad_detail"),

    # Студент
    path("olympiad/<int:pk>/register/", views.register_for_olympiad, name="register_for_olympiad"),

    # Преподаватель
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/olympiad/<int:pk>/regulation/", views.upload_regulation, name="upload_regulation"),
    path("teacher/protocol/create/", views.create_protocol, name="create_protocol"),
    path("teacher/protocol/<int:pk>/edit/", views.protocol_edit, name="protocol_edit"),
    path("teacher/protocol/<int:pk>/prepared/", views.protocol_set_prepared, name="protocol_set_prepared"),
    path("teacher/protocol/<int:pk>/recall/", views.protocol_recall, name="protocol_recall"),
    path("teacher/olympiad/<int:olympiad_pk>/certificate/", views.certificate_add, name="certificate_add"),

    # Администратор
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/olympiad/create/", views.olympiad_create, name="olympiad_create"),
    path("manage/olympiad/<int:pk>/edit/", views.olympiad_edit, name="olympiad_edit"),
    path("manage/protocol/<int:pk>/publish/", views.protocol_publish, name="protocol_publish"),

    # Отчёты
    path("report/protocol/<int:pk>/", views.report_protocol, name="report_protocol"),
    path("report/annual/<int:year>/", views.report_annual, name="report_annual"),
]
