# -*- coding: utf-8 -*-

from django.apps import AppConfig


class ReporterCoreAppConfig(AppConfig):
    name = 'reporter.core'
    verbose_name = "core"

    def ready(self):
        from . import signals  # @UnusedImport
