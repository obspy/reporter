from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from taggit.models import Tag

from . import models


class DocumentTypeFilter(admin.SimpleListFilter):
    title = "Document type"
    parameter_name = "type"

    def lookups(self, request, model_admin):
        return (
            ("json", "JSON"),
            ("xml", "XML"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        # filter
        if value == "json":
            return queryset.filter(xml=None)
        elif value == "xml":
            return queryset.exclude(xml=None)
        return queryset


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
        "display_document_type",
    ]
    search_fields = [
        "installed",
        "node",
        "system",
        "architecture",
        "version",
    ]
    list_filter = [
        DocumentTypeFilter,
        "system",
        "architecture",
        "version",
    ]
    date_hierarchy = "datetime"
    readonly_fields = ["id"]

    @admin.display(description="Type")
    def display_document_type(self, obj):
        if obj.json:
            return "JSON"
        elif obj.xml:
            return "XML"
        return "-"


@admin.register(models.SelectedNode)
class SelectedNodeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.MenuItem)
class MenuItemAdmin(DjangoMpttAdmin):
    list_display = ["name"]


# remove TaggedItemInline from default TagAdmin
admin.site.unregister(Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}
