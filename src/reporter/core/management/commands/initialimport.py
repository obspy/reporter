# -*- coding: utf-8 -*-
"""
Management command to import old test reports and default selected nodes.
"""

from django.core.management.base import BaseCommand
from reporter.core.utils import import_old_reports, set_default_selected_nodes


class Command(BaseCommand):
    args = ""
    help = "Import initial test reports and nodes"  # @ReservedAssignment

    def handle(self, *args, **options):  # @UnusedVariable
        import_old_reports()
        set_default_selected_nodes()
