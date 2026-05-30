from django import forms

from .models import Olympiad, Protocol, Result, Certificate


class OlympiadForm(forms.ModelForm):
    """Карточка олимпиады (администратор)."""

    class Meta:
        model = Olympiad
        fields = (
            "title", "description", "year", "start_date", "end_date",
            "registration_deadline", "location", "level", "responsible_teacher",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "registration_deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class RegulationForm(forms.ModelForm):
    """Прикрепление положения и заданий преподавателем."""

    class Meta:
        model = Olympiad
        fields = ("regulation_file", "tasks_file")


class ProtocolForm(forms.ModelForm):
    """Создание протокола преподавателем."""

    class Meta:
        model = Protocol
        fields = ("olympiad",)


class ResultForm(forms.ModelForm):
    """Добавление/редактирование результата участника."""

    class Meta:
        model = Result
        fields = ("student", "score", "place", "result_type")


class CertificateForm(forms.ModelForm):
    """Бланк сертификата/грамоты."""

    class Meta:
        model = Certificate
        fields = ("title", "cert_type", "template_file")
