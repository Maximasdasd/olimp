"""Вьюхи фронтенда. Каждая страница берёт данные из FastAPI-бэкенда."""
import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from . import fastapi_client as api
from .decorators import (
    login_required, admin_required, teacher_required, student_required,
)


# ============ АУТЕНТИФИКАЦИЯ ============

def login_view(request):
    """Вход по логину и паролю (через FastAPI)."""
    if api.get_current_user(request):
        return redirect("olympiad_list")
    if request.method == "POST":
        ok, error = api.login_to_fastapi(
            request, request.POST.get("username"), request.POST.get("password")
        )
        if ok:
            messages.success(request, "Вы вошли в систему.")
            return redirect(request.GET.get("next") or "olympiad_list")
        messages.error(request, error or "Ошибка входа")
    return render(request, "core/login.html")


def register_view(request):
    """Регистрация студента (через FastAPI)."""
    if api.get_current_user(request):
        return redirect("olympiad_list")
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "full_name": request.POST.get("full_name"),
            "password": request.POST.get("password"),
            "role": "student",
        }
        ok, error = api.register_student(request, payload)
        if ok:
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("olympiad_list")
        messages.error(request, error or "Ошибка регистрации")
    return render(request, "core/register.html")


def logout_view(request):
    """Выход."""
    api.logout(request)
    messages.success(request, "Вы вышли из системы.")
    return redirect("olympiad_list")


# ============ ПУБЛИЧНАЯ ЧАСТЬ ============

def olympiad_list(request):
    """Список всех олимпиад с фильтром по году (доступно всем)."""
    params = {}
    year = request.GET.get("year")
    if year:
        params["year"] = year
    resp = api.api_get(request, "/api/olympiads", params=params)
    olympiads = resp.json() if resp.status_code == 200 else []
    years = sorted({o["year"] for o in olympiads}, reverse=True) if not year else None
    if years is None:
        # при фильтре получаем полный список отдельно ради списка годов
        all_resp = api.api_get(request, "/api/olympiads")
        if all_resp.status_code == 200:
            years = sorted({o["year"] for o in all_resp.json()}, reverse=True)
        else:
            years = []
    return render(request, "core/olympiad_list.html", {
        "olympiads": olympiads,
        "years": years,
        "selected_year": int(year) if year and year.isdigit() else None,
    })


def olympiad_detail(request, pk):
    """Карточка олимпиады: данные, протокол победителей."""
    resp = api.api_get(request, f"/api/olympiads/{pk}")
    if resp.status_code != 200:
        messages.error(request, "Олимпиада не найдена.")
        return redirect("olympiad_list")
    olympiad = resp.json()

    results = []
    res_resp = api.api_get(request, f"/api/olympiads/{pk}/results")
    if res_resp.status_code == 200:
        results = res_resp.json()

    return render(request, "core/olympiad_detail.html", {
        "olympiad": olympiad,
        "results": results,
        "has_protocol": olympiad.get("is_protocol_published"),
    })


# ============ СТУДЕНТ ============

@student_required
def register_for_olympiad(request, pk):
    """Запись студента на олимпиаду."""
    if request.method == "POST":
        resp = api.api_post(request, f"/api/student/register/{pk}")
        if resp.status_code == 200:
            messages.success(request, "Вы записаны на олимпиаду.")
        else:
            detail = "Не удалось записаться"
            try:
                detail = resp.json().get("detail", detail)
            except ValueError:
                pass
            messages.error(request, detail)
    return redirect("olympiad_detail", pk=pk)


@student_required
def my_profile(request):
    """Личный кабинет студента: записи и результаты."""
    olympiads_resp = api.api_get(request, "/api/student/my-olympiads")
    results_resp = api.api_get(request, "/api/student/my-results")
    return render(request, "core/profile.html", {
        "registrations": olympiads_resp.json() if olympiads_resp.status_code == 200 else [],
        "results": results_resp.json() if results_resp.status_code == 200 else [],
    })


# ============ ПРЕПОДАВАТЕЛЬ ============

@teacher_required
def teacher_dashboard(request):
    """Кабинет преподавателя: список протоколов (из общих по бэкенду)."""
    protocols = []
    resp = api.api_get(request, "/api/admin/protocols")
    if resp.status_code == 200:
        protocols = resp.json()
    olympiads_resp = api.api_get(request, "/api/olympiads")
    olympiads = olympiads_resp.json() if olympiads_resp.status_code == 200 else []
    return render(request, "core/teacher_dashboard.html", {
        "protocols": protocols,
        "olympiads": olympiads,
    })


@teacher_required
def create_student(request):
    """Создание учетной записи студента преподавателем."""
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "full_name": request.POST.get("full_name"),
            "password": request.POST.get("password"),
            "institution": request.POST.get("institution", ""),
            "education_level": request.POST.get("education_level", ""),
            "specialty": request.POST.get("specialty", ""),
        }
        course = request.POST.get("course")
        if course:
            payload["course"] = int(course)
        resp = api.api_post(request, "/api/teacher/students", json=payload)
        if resp.status_code == 200:
            messages.success(request, "Студент создан.")
            return redirect("teacher_dashboard")
        messages.error(request, _detail(resp, "Не удалось создать студента"))
    return render(request, "core/student_form.html")


@teacher_required
def create_protocol(request):
    """Создание протокола."""
    if request.method == "POST":
        payload = {"olympiad_id": int(request.POST.get("olympiad_id"))}
        resp = api.api_post(request, "/api/teacher/protocols", json=payload)
        if resp.status_code == 200:
            messages.success(request, "Протокол создан.")
            return redirect("teacher_dashboard")
        messages.error(request, _detail(resp, "Не удалось создать протокол"))
    olympiads_resp = api.api_get(request, "/api/olympiads")
    olympiads = olympiads_resp.json() if olympiads_resp.status_code == 200 else []
    return render(request, "core/protocol_form.html", {"olympiads": olympiads})


@teacher_required
def add_result(request, protocol_id):
    """Добавление результата в протокол."""
    if request.method == "POST":
        payload = {
            "student_id": int(request.POST.get("student_id")),
            "score": float(request.POST.get("score") or 0),
            "result_type": request.POST.get("result_type", "participant"),
        }
        place = request.POST.get("place")
        if place:
            payload["place"] = int(place)
        resp = api.api_post(request, f"/api/teacher/protocols/{protocol_id}/results", json=payload)
        if resp.status_code == 200:
            messages.success(request, "Результат добавлен.")
        else:
            messages.error(request, _detail(resp, "Не удалось добавить результат"))
    return redirect("teacher_dashboard")


@teacher_required
def set_protocol_prepared(request, protocol_id):
    """Перевод протокола в статус «подготовлен»."""
    if request.method == "POST":
        resp = api.api_put(
            request, f"/api/teacher/protocols/{protocol_id}/status",
            json={"status": "prepared"},
        )
        if resp.status_code == 200:
            messages.success(request, "Протокол подготовлен.")
        else:
            messages.error(request, _detail(resp, "Не удалось изменить статус"))
    return redirect("teacher_dashboard")


@teacher_required
def recall_protocol(request, protocol_id):
    """Отзыв протокола (возврат в «формируется»)."""
    if request.method == "POST":
        resp = api.api_put(
            request, f"/api/teacher/protocols/{protocol_id}/status",
            json={"status": "draft"},
        )
        if resp.status_code == 200:
            messages.success(request, "Протокол отозван для изменений.")
        else:
            messages.error(request, _detail(resp, "Не удалось отозвать протокол"))
    return redirect("teacher_dashboard")


# ============ АДМИНИСТРАТОР ============

@admin_required
def admin_dashboard(request):
    """Панель администратора: протоколы и публикация."""
    protocols = []
    resp = api.api_get(request, "/api/admin/protocols")
    if resp.status_code == 200:
        protocols = resp.json()
    return render(request, "core/admin_dashboard.html", {"protocols": protocols})


@admin_required
def create_olympiad(request):
    """Заполнение карточки олимпиады."""
    if request.method == "POST":
        payload = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description", ""),
            "year": int(request.POST.get("year")),
            "start_date": request.POST.get("start_date") or None,
            "end_date": request.POST.get("end_date") or None,
            "level": request.POST.get("level", ""),
        }
        teacher_id = request.POST.get("teacher_id")
        if teacher_id:
            payload["teacher_id"] = int(teacher_id)
        resp = api.api_post(request, "/api/admin/olympiads", json=payload)
        if resp.status_code == 200:
            messages.success(request, "Олимпиада создана.")
            return redirect("admin_dashboard")
        messages.error(request, _detail(resp, "Не удалось создать олимпиаду"))
    return render(request, "core/olympiad_form.html")


@admin_required
def create_teacher(request):
    """Создание учетной записи преподавателя."""
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "full_name": request.POST.get("full_name"),
            "password": request.POST.get("password"),
            "department": request.POST.get("department", ""),
            "position": request.POST.get("position", ""),
        }
        resp = api.api_post(request, "/api/admin/teachers", json=payload)
        if resp.status_code == 200:
            messages.success(request, "Преподаватель создан.")
            return redirect("admin_dashboard")
        messages.error(request, _detail(resp, "Не удалось создать преподавателя"))
    return render(request, "core/teacher_form.html")


@admin_required
def publish_protocol(request, protocol_id):
    """Публикация подготовленного протокола."""
    if request.method == "POST":
        resp = api.api_put(request, f"/api/admin/protocols/{protocol_id}/publish")
        if resp.status_code == 200:
            messages.success(request, "Протокол опубликован.")
        else:
            messages.error(request, _detail(resp, "Не удалось опубликовать протокол"))
    return redirect("admin_dashboard")


# ============ ОТЧЕТЫ ============

@admin_required
def annual_report(request, year):
    """Годовой отчёт (CSV для Excel) — данные из FastAPI."""
    resp = api.api_get(request, "/api/olympiads", params={"year": year})
    olympiads = resp.json() if resp.status_code == 200 else []

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="annual_{year}.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow([f"Годовой отчёт за {year} год"])
    writer.writerow(["Олимпиада", "Год", "Уровень", "Протокол опубликован"])
    for o in olympiads:
        writer.writerow([
            o.get("title"), o.get("year"), o.get("level", ""),
            "да" if o.get("is_protocol_published") else "нет",
        ])
    return response


# --- утилита ------------------------------------------------------------
def _detail(resp, default):
    """Извлечь сообщение об ошибке из ответа FastAPI."""
    try:
        return resp.json().get("detail", default)
    except ValueError:
        return default
