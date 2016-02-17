# -*- coding: utf-8 -*-

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = "core"

    def ready(self):
        import reporter.core.signals  # @UnusedImport
