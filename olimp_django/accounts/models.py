from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь с ролью. Вход выполняется по логину и паролю."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        TEACHER = "teacher", "Преподаватель"
        STUDENT = "student", "Студент"

    role = models.CharField(
        "Роль", max_length=20, choices=Role.choices, default=Role.STUDENT
    )
    full_name = models.CharField("ФИО", max_length=200, blank=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def display_name(self):
        return self.full_name or self.get_full_name() or self.username

    def __str__(self):
        return f"{self.display_name()} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """Профиль студента (ТЗ: ФИО, дата рождения, email, учебное заведение и т.д.)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    institution = models.CharField("Учебное заведение", max_length=200, blank=True)
    education_level = models.CharField("Уровень образования", max_length=100, blank=True)
    course = models.PositiveIntegerField("Курс обучения", null=True, blank=True)
    specialty = models.CharField("Специальность", max_length=150, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Профиль студента"
        verbose_name_plural = "Профили студентов"

    def __str__(self):
        return f"Студент: {self.user.display_name()}"


class TeacherProfile(models.Model):
    """Профиль преподавателя."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    department = models.CharField("Кафедра/отделение", max_length=150, blank=True)
    position = models.CharField("Должность", max_length=150, blank=True)
    academic_degree = models.CharField("Ученая степень", max_length=100, blank=True)

    class Meta:
        verbose_name = "Профиль преподавателя"
        verbose_name_plural = "Профили преподавателей"

    def __str__(self):
        return f"Преподаватель: {self.user.display_name()}"
