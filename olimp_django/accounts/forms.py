from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, StudentProfile, TeacherProfile


class StudentSelfRegisterForm(UserCreationForm):
    """Самостоятельная регистрация студента (вход по логину и паролю)."""

    full_name = forms.CharField(label="ФИО", max_length=200)
    email = forms.EmailField(label="Электронная почта")

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            StudentProfile.objects.create(user=user)
        return user


class StudentProfileForm(forms.ModelForm):
    """Редактирование профиля студентом."""

    full_name = forms.CharField(label="ФИО", max_length=200, required=False)
    email = forms.EmailField(label="Электронная почта", required=False)

    class Meta:
        model = StudentProfile
        fields = (
            "birth_date", "institution", "education_level",
            "course", "specialty", "phone",
        )
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["full_name"].initial = self.instance.user.full_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.full_name = self.cleaned_data.get("full_name", user.full_name)
        user.email = self.cleaned_data.get("email", user.email)
        if commit:
            user.save()
            profile.save()
        return profile


class TeacherCreateForm(UserCreationForm):
    """Создание учетной записи преподавателя администратором."""

    full_name = forms.CharField(label="ФИО", max_length=200)
    email = forms.EmailField(label="Электронная почта")
    department = forms.CharField(label="Кафедра/отделение", max_length=150, required=False)
    position = forms.CharField(label="Должность", max_length=150, required=False)

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                department=self.cleaned_data.get("department", ""),
                position=self.cleaned_data.get("position", ""),
            )
        return user


class StudentCreateForm(UserCreationForm):
    """Создание учетной записи студента преподавателем (ТЗ)."""

    full_name = forms.CharField(label="ФИО", max_length=200)
    email = forms.EmailField(label="Электронная почта")
    birth_date = forms.DateField(
        label="Дата рождения", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    institution = forms.CharField(label="Учебное заведение", max_length=200, required=False)
    education_level = forms.CharField(label="Уровень образования", max_length=100, required=False)
    course = forms.IntegerField(label="Курс обучения", required=False)
    specialty = forms.CharField(label="Специальность", max_length=150, required=False)

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                birth_date=self.cleaned_data.get("birth_date"),
                institution=self.cleaned_data.get("institution", ""),
                education_level=self.cleaned_data.get("education_level", ""),
                course=self.cleaned_data.get("course"),
                specialty=self.cleaned_data.get("specialty", ""),
            )
        return user


class TeacherEditForm(forms.ModelForm):
    """Редактирование существующей учетной записи (ТЗ: функция администратора)."""

    class Meta:
        model = User
        fields = ("full_name", "email", "is_active")
