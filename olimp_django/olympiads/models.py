from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Olympiad(models.Model):
    """Карточка олимпиады (ТЗ: название, ответственный преподаватель, даты)."""

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    year = models.PositiveIntegerField("Год проведения")
    start_date = models.DateField("Дата начала", null=True, blank=True)
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    registration_deadline = models.DateField("Дедлайн регистрации", null=True, blank=True)
    location = models.CharField("Место проведения", max_length=200, blank=True)
    level = models.CharField("Уровень", max_length=100, blank=True)

    responsible_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="responsible_olympiads", verbose_name="Ответственный преподаватель",
        limit_choices_to={"role": "teacher"},
    )
    # Положение по олимпиаде (создаёт/прикрепляет преподаватель)
    regulation_file = models.FileField(
        "Положение", upload_to="regulations/", null=True, blank=True
    )
    # Задания прошлых лет
    tasks_file = models.FileField(
        "Задания прошлых лет", upload_to="tasks/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Олимпиада"
        verbose_name_plural = "Олимпиады"
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def has_published_protocol(self):
        return self.protocols.filter(status=Protocol.Status.PUBLISHED).exists()

    @property
    def published_protocol(self):
        return self.protocols.filter(status=Protocol.Status.PUBLISHED).first()


class Registration(models.Model):
    """Запись студента на олимпиаду."""

    olympiad = models.ForeignKey(
        Olympiad, on_delete=models.CASCADE, related_name="registrations",
        verbose_name="Олимпиада",
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registrations",
        verbose_name="Студент",
    )
    registered_at = models.DateTimeField("Дата записи", auto_now_add=True)

    class Meta:
        verbose_name = "Запись на олимпиаду"
        verbose_name_plural = "Записи на олимпиады"
        unique_together = ("olympiad", "student")

    def __str__(self):
        return f"{self.student} → {self.olympiad}"


class Protocol(models.Model):
    """Протокол олимпиады. Статусы по ТЗ: формируется, подготовлен, опубликован."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Формируется"
        PREPARED = "prepared", "Подготовлен"
        PUBLISHED = "published", "Опубликован"

    olympiad = models.ForeignKey(
        Olympiad, on_delete=models.CASCADE, related_name="protocols",
        verbose_name="Олимпиада",
    )
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_protocols", verbose_name="Преподаватель",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Протокол"
        verbose_name_plural = "Протоколы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Протокол: {self.olympiad} [{self.get_status_display()}]"


class Result(models.Model):
    """Результат участника в протоколе (баллы + тип результата)."""

    class ResultType(models.TextChoices):
        WINNER = "winner", "Победитель"
        PRIZE_WINNER = "prize_winner", "Призёр"
        PARTICIPANT = "participant", "Участник"

    protocol = models.ForeignKey(
        Protocol, on_delete=models.CASCADE, related_name="results",
        verbose_name="Протокол",
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="results",
        verbose_name="Студент",
    )
    score = models.FloatField("Баллы", default=0)
    place = models.PositiveIntegerField("Место", null=True, blank=True)
    result_type = models.CharField(
        "Тип результата", max_length=20,
        choices=ResultType.choices, default=ResultType.PARTICIPANT,
    )

    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"
        ordering = ["place", "-score"]

    def __str__(self):
        return f"{self.student}: {self.score} б. ({self.get_result_type_display()})"


class Certificate(models.Model):
    """Бланк сертификата/грамоты за участие (к одной олимпиаде — любое количество)."""

    class CertType(models.TextChoices):
        DIPLOMA = "diploma", "Грамота"
        CERTIFICATE = "certificate", "Сертификат"
        DEGREE = "degree", "Диплом"

    olympiad = models.ForeignKey(
        Olympiad, on_delete=models.CASCADE, related_name="certificates",
        verbose_name="Олимпиада",
    )
    title = models.CharField("Название бланка", max_length=200)
    cert_type = models.CharField(
        "Тип", max_length=20, choices=CertType.choices, default=CertType.CERTIFICATE
    )
    template_file = models.FileField(
        "Файл бланка", upload_to="certificates/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Бланк сертификата/грамоты"
        verbose_name_plural = "Бланки сертификатов/грамот"

    def __str__(self):
        return f"{self.get_cert_type_display()}: {self.title}"
