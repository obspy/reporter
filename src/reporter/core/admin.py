from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from . import models


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "errors",
        "failures",
        "skipped",
        "tests",
        "modules",
        "installed",
        "node",
        "system",
        "architecture",
        "version",
        "timetaken",
        "datetime",
    ]
    search_fields = [
        "installed",
        "node",
        "system",
        "architecture",
        "version",
    ]
    list_filter = [
        "system",
        "architecture",
        "version",
    ]
    date_hierarchy = "datetime"
    readonly_fields = ["id"]


@admin.register(models.SelectedNode)
class SelectedNodeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.MenuItem)
class MenuItemAdmin(DjangoMpttAdmin):
    list_display = ["name"]
