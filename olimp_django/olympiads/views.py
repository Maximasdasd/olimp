import csv

from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .models import Olympiad, Registration, Protocol, Result, Certificate
from .forms import (
    OlympiadForm, RegulationForm, ProtocolForm, ResultForm, CertificateForm,
)
from .decorators import admin_required, teacher_required, student_required


# ============ ПУБЛИЧНАЯ ЧАСТЬ (незарегистрированный пользователь) ============

def olympiad_list(request):
    """Список всех олимпиад с фильтром по году (доступно всем)."""
    olympiads = Olympiad.objects.all()
    year = request.GET.get("year")
    if year:
        olympiads = olympiads.filter(year=year)
    years = (
        Olympiad.objects.values_list("year", flat=True)
        .distinct().order_by("-year")
    )
    return render(request, "olympiads/list.html", {
        "olympiads": olympiads,
        "years": years,
        "selected_year": int(year) if year and year.isdigit() else None,
    })


def olympiad_detail(request, pk):
    """Карточка олимпиады: положение, задания, протокол победителей."""
    olympiad = get_object_or_404(Olympiad, pk=pk)
    protocol = olympiad.published_protocol
    results = protocol.results.select_related("student") if protocol else []
    is_registered = (
        request.user.is_authenticated
        and Registration.objects.filter(olympiad=olympiad, student=request.user).exists()
    )
    return render(request, "olympiads/detail.html", {
        "olympiad": olympiad,
        "protocol": protocol,
        "results": results,
        "is_registered": is_registered,
    })


# ============ СТУДЕНТ ============

@student_required
def register_for_olympiad(request, pk):
    """Запись студента на олимпиаду."""
    olympiad = get_object_or_404(Olympiad, pk=pk)
    if request.method == "POST":
        _, created = Registration.objects.get_or_create(
            olympiad=olympiad, student=request.user
        )
        if created:
            messages.success(request, f"Вы записаны на «{olympiad.title}».")
        else:
            messages.info(request, "Вы уже записаны на эту олимпиаду.")
    return redirect("olympiad_detail", pk=pk)


# ============ ПРЕПОДАВАТЕЛЬ ============

@teacher_required
def teacher_dashboard(request):
    """Панель преподавателя: его олимпиады и протоколы."""
    protocols = (
        Protocol.objects.filter(teacher=request.user)
        .select_related("olympiad")
    )
    olympiads = Olympiad.objects.filter(responsible_teacher=request.user)
    return render(request, "teacher/dashboard.html", {
        "protocols": protocols,
        "olympiads": olympiads,
    })


@teacher_required
def upload_regulation(request, pk):
    """Прикрепление положения и заданий к олимпиаде."""
    olympiad = get_object_or_404(Olympiad, pk=pk)
    if request.method == "POST":
        form = RegulationForm(request.POST, request.FILES, instance=olympiad)
        if form.is_valid():
            form.save()
            messages.success(request, "Файлы загружены.")
            return redirect("teacher_dashboard")
    else:
        form = RegulationForm(instance=olympiad)
    return render(request, "teacher/upload_regulation.html", {
        "form": form, "olympiad": olympiad,
    })


@teacher_required
def create_protocol(request):
    """Создание протокола."""
    if request.method == "POST":
        form = ProtocolForm(request.POST)
        if form.is_valid():
            protocol = form.save(commit=False)
            protocol.teacher = request.user
            protocol.save()
            messages.success(request, "Протокол создан.")
            return redirect("protocol_edit", pk=protocol.pk)
    else:
        form = ProtocolForm()
    return render(request, "teacher/protocol_form.html", {"form": form})


@teacher_required
def protocol_edit(request, pk):
    """Добавление результатов в протокол и смена статуса."""
    protocol = get_object_or_404(Protocol, pk=pk)
    if protocol.status == Protocol.Status.PUBLISHED:
        messages.warning(request, "Опубликованный протокол нельзя редактировать.")
        return redirect("teacher_dashboard")

    if request.method == "POST":
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.protocol = protocol
            result.save()
            messages.success(request, "Результат добавлен.")
            return redirect("protocol_edit", pk=pk)
    else:
        form = ResultForm()

    return render(request, "teacher/protocol_edit.html", {
        "protocol": protocol,
        "form": form,
        "results": protocol.results.select_related("student"),
    })


@teacher_required
def protocol_set_prepared(request, pk):
    """Перевод протокола в статус «подготовлен»."""
    protocol = get_object_or_404(Protocol, pk=pk)
    if request.method == "POST":
        protocol.status = Protocol.Status.PREPARED
        protocol.save()
        messages.success(request, "Протокол подготовлен и готов к публикации.")
    return redirect("teacher_dashboard")


@teacher_required
def protocol_recall(request, pk):
    """Отзыв протокола (ТЗ: можно отозвать только «подготовленный»)."""
    protocol = get_object_or_404(Protocol, pk=pk)
    if request.method == "POST":
        if protocol.status == Protocol.Status.PREPARED:
            protocol.status = Protocol.Status.DRAFT
            protocol.save()
            messages.success(request, "Протокол отозван для изменений.")
        else:
            messages.error(request, "Отозвать можно только подготовленный протокол.")
    return redirect("teacher_dashboard")


@teacher_required
def certificate_add(request, olympiad_pk):
    """Добавление бланка сертификата/грамоты к олимпиаде."""
    olympiad = get_object_or_404(Olympiad, pk=olympiad_pk)
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.olympiad = olympiad
            cert.save()
            messages.success(request, "Бланк добавлен.")
            return redirect("teacher_dashboard")
    else:
        form = CertificateForm()
    return render(request, "teacher/certificate_form.html", {
        "form": form, "olympiad": olympiad,
    })


# ============ АДМИНИСТРАТОР ============

@admin_required
def admin_dashboard(request):
    """Панель администратора."""
    return render(request, "admin_panel/dashboard.html", {
        "olympiads_count": Olympiad.objects.count(),
        "protocols": Protocol.objects.select_related("olympiad").all(),
    })


@admin_required
def olympiad_create(request):
    """Заполнение карточки олимпиады."""
    if request.method == "POST":
        form = OlympiadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Олимпиада создана.")
            return redirect("admin_dashboard")
    else:
        form = OlympiadForm()
    return render(request, "admin_panel/olympiad_form.html", {"form": form, "is_new": True})


@admin_required
def olympiad_edit(request, pk):
    """Редактирование карточки олимпиады."""
    olympiad = get_object_or_404(Olympiad, pk=pk)
    if request.method == "POST":
        form = OlympiadForm(request.POST, instance=olympiad)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("admin_dashboard")
    else:
        form = OlympiadForm(instance=olympiad)
    return render(request, "admin_panel/olympiad_form.html", {"form": form, "is_new": False})


@admin_required
def protocol_publish(request, pk):
    """Публикация протокола (только из статуса «подготовлен»)."""
    protocol = get_object_or_404(Protocol, pk=pk)
    if request.method == "POST":
        if protocol.status == Protocol.Status.PREPARED:
            protocol.status = Protocol.Status.PUBLISHED
            protocol.save()
            messages.success(request, "Протокол опубликован.")
        else:
            messages.error(request, "Опубликовать можно только подготовленный протокол.")
    return redirect("admin_dashboard")


# ============ ОТЧЕТЫ (Word/Excel — выгрузка CSV/таблицы) ============

@teacher_required
def report_protocol(request, pk):
    """Отчёт по протоколу олимпиады (CSV, открывается в Excel)."""
    protocol = get_object_or_404(Protocol, pk=pk)
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="protocol_{pk}.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow([f"Протокол олимпиады: {protocol.olympiad.title} ({protocol.olympiad.year})"])
    writer.writerow(["Студент", "Баллы", "Место", "Результат"])
    for r in protocol.results.select_related("student"):
        writer.writerow([
            r.student.display_name(), r.score, r.place or "",
            r.get_result_type_display(),
        ])
    return response


@admin_required
def report_annual(request, year):
    """Годовой отчёт участия в олимпиадном движении (CSV)."""
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="annual_{year}.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow([f"Годовой отчёт за {year} год"])
    writer.writerow(["Олимпиада", "Участников", "Победителей", "Призёров"])
    for olympiad in Olympiad.objects.filter(year=year):
        results = Result.objects.filter(protocol__olympiad=olympiad)
        writer.writerow([
            olympiad.title,
            results.count(),
            results.filter(result_type=Result.ResultType.WINNER).count(),
            results.filter(result_type=Result.ResultType.PRIZE_WINNER).count(),
        ])
    return response
