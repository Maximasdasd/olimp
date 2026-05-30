"""Наполнение БД демонстрационными данными.

Запуск: python manage.py seed_demo
Создаёт администратора, преподавателя, студента и пару олимпиад.
"""
from datetime import date

from django.core.management.base import BaseCommand

from accounts.models import User, StudentProfile, TeacherProfile
from olympiads.models import Olympiad, Protocol, Result, Registration


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные (пользователи, олимпиады, протоколы)."

    def handle(self, *args, **options):
        # Администратор
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"role": User.Role.ADMIN, "full_name": "Администратор Системы",
                      "email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin123")
            admin.save()

        # Преподаватель
        teacher, created = User.objects.get_or_create(
            username="teacher",
            defaults={"role": User.Role.TEACHER, "full_name": "Иванов Иван Иванович",
                      "email": "teacher@example.com"},
        )
        if created:
            teacher.set_password("teacher123")
            teacher.save()
            TeacherProfile.objects.create(user=teacher, department="Информатика", position="Доцент")

        # Студент
        student, created = User.objects.get_or_create(
            username="student",
            defaults={"role": User.Role.STUDENT, "full_name": "Петров Пётр Петрович",
                      "email": "student@example.com"},
        )
        if created:
            student.set_password("student123")
            student.save()
            StudentProfile.objects.create(
                user=student, institution="ЕМК", education_level="СПО",
                course=3, specialty="Информационные системы",
            )

        # Олимпиады
        o1, _ = Olympiad.objects.get_or_create(
            title="Олимпиада по программированию", year=2025,
            defaults={"level": "Региональная", "responsible_teacher": teacher,
                      "start_date": date(2025, 3, 1), "end_date": date(2025, 3, 2),
                      "description": "Командная олимпиада по алгоритмам."},
        )
        Olympiad.objects.get_or_create(
            title="Конкурс веб-разработки", year=2024,
            defaults={"level": "Городская", "responsible_teacher": teacher,
                      "start_date": date(2024, 4, 10), "end_date": date(2024, 4, 11)},
        )

        # Запись и опубликованный протокол
        Registration.objects.get_or_create(olympiad=o1, student=student)
        protocol, created = Protocol.objects.get_or_create(
            olympiad=o1, defaults={"teacher": teacher, "status": Protocol.Status.PUBLISHED},
        )
        if created:
            Result.objects.create(
                protocol=protocol, student=student, score=95, place=1,
                result_type=Result.ResultType.WINNER,
            )

        self.stdout.write(self.style.SUCCESS(
            "Демо-данные созданы.\n"
            "  admin / admin123 (администратор)\n"
            "  teacher / teacher123 (преподаватель)\n"
            "  student / student123 (студент)"
        ))
