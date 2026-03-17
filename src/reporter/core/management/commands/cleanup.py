"""
Management command to cleanup database.
"""

import datetime

from django.core.management.base import BaseCommand

from reporter.core import models


class Command(BaseCommand):
    args = "months"
    help = "Cleanup database"

    def add_arguments(self, parser):
        parser.add_argument("months", default=12, type=int)

    def handle(self, months, **options):
        # not exact but good enough
        days = 30 * months
        dt = datetime.datetime.now() - datetime.timedelta(days=days)
        models.Report.objects.filter(datetime__lt=dt).delete()
