from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    StudentSelfRegisterForm, StudentProfileForm,
    TeacherCreateForm, StudentCreateForm, TeacherEditForm,
)
from .models import StudentProfile, User
from olympiads.decorators import admin_required, teacher_required
from olympiads.models import Registration, Result


def register(request):
    """Самостоятельная регистрация студента."""
    if request.user.is_authenticated:
        return redirect("olympiad_list")
    if request.method == "POST":
        form = StudentSelfRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("olympiad_list")
    else:
        form = StudentSelfRegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    """Личный кабинет студента: профиль, записи и результаты."""
    profile_obj, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile")
    else:
        form = StudentProfileForm(instance=profile_obj)

    registrations = (
        Registration.objects.filter(student=request.user)
        .select_related("olympiad")
    )
    results = (
        Result.objects.filter(student=request.user)
        .select_related("protocol__olympiad")
    )
    return render(request, "accounts/profile.html", {
        "form": form,
        "registrations": registrations,
        "results": results,
    })


# ============ АДМИНИСТРАТОР: учетные записи преподавателей ============

@admin_required
def teacher_list(request):
    """Список преподавателей (создание и редактирование)."""
    teachers = User.objects.filter(role=User.Role.TEACHER).order_by("full_name")
    return render(request, "admin_panel/teacher_list.html", {"teachers": teachers})


@admin_required
def teacher_create(request):
    """Создание учетной записи преподавателя."""
    if request.method == "POST":
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Преподаватель создан.")
            return redirect("teacher_list")
    else:
        form = TeacherCreateForm()
    return render(request, "accounts/user_form.html", {
        "form": form, "title": "Создание преподавателя",
    })


@admin_required
def teacher_edit(request, pk):
    """Редактирование существующей учетной записи преподавателя."""
    teacher = get_object_or_404(User, pk=pk, role=User.Role.TEACHER)
    if request.method == "POST":
        form = TeacherEditForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Учетная запись обновлена.")
            return redirect("teacher_list")
    else:
        form = TeacherEditForm(instance=teacher)
    return render(request, "accounts/user_form.html", {
        "form": form, "title": f"Редактирование: {teacher.display_name()}",
    })


# ============ ПРЕПОДАВАТЕЛЬ: учетные записи студентов ============

@teacher_required
def student_create(request):
    """Создание учетной записи студента преподавателем."""
    if request.method == "POST":
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Студент создан.")
            return redirect("teacher_dashboard")
    else:
        form = StudentCreateForm()
    return render(request, "accounts/user_form.html", {
        "form": form, "title": "Создание студента",
    })
