# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.apps import AppConfig


class ReporterCoreAppConfig(AppConfig):
    name = 'reporter.core'
    verbose_name = "core"

    def ready(self):
        from . import signals  # @UnusedImport
