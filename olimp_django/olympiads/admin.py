from django.contrib import admin

from .models import Olympiad, Registration, Protocol, Result, Certificate


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0


@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "responsible_teacher", "level")
    list_filter = ("year", "level")
    search_fields = ("title",)
    inlines = [CertificateInline]


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ("olympiad", "teacher", "status", "created_at")
    list_filter = ("status",)
    inlines = [ResultInline]


admin.site.register(Registration)
admin.site.register(Result)
admin.site.register(Certificate)
