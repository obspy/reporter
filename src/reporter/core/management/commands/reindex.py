# -*- coding: utf-8 -*-
"""
Management command to reindex database using XML stored document.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.core.management.base import BaseCommand

from reporter.core import models, utils


class Command(BaseCommand):
    args = ""
    help = "Reindex database using XML stored document"  # @ReservedAssignment

    def handle(self, **options):  # @UnusedVariable
        for report in models.Report.objects.order_by('-id'):
            print(report.id)
            options = utils.parse_report_xml(report.xml)
            for key, value in options.items():
                if key == 'tags':
                    report.tags.all().delete()
                    report.tags.add(*value)
                else:
                    setattr(report, key, value)
            report.save()
