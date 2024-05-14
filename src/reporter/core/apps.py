from django.apps import AppConfig


class ReporterCoreAppConfig(AppConfig):
    name = "reporter.core"
    verbose_name = "core"

    def ready(self):
        from . import signals
