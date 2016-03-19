# -*- coding: utf-8 -*-
"""
Management command to reindex database using XML stored document.
"""
from django.core.management.base import BaseCommand

from reporter.core.models import Report
from reporter.core.utils import parse_report_xml


class Command(BaseCommand):
    args = ""
    help = "Reindex database using XML stored document"  # @ReservedAssignment

    def handle(self, **options):  # @UnusedVariable
        for report in Report.objects.order_by('-id'):
            print(report.id)
            options = parse_report_xml(report.xml)
            for key, value in options.items():
                if key == 'tags':
                    report.tags.all().delete()
                    report.tags.add(*value)
                else:
                    setattr(report, key, value)
            report.save()
