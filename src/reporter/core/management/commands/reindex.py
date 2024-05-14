"""
Management command to reindex database.
"""

from django.core.management.base import BaseCommand

from reporter.core import models, utils


class Command(BaseCommand):
    args = "pk or pk:pk"
    help = "Reindex database"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="+")

    def handle(self, *args, **options):
        pks = list(args)
        for pk in pks:
            if isinstance(pk, str) and ":" in pk:
                start, end = pk.split(":")
                new_pks = range(int(start), int(end))
            else:
                new_pks = [int(pk)]
            for new_pk in new_pks:
                try:
                    report = models.Report.objects.get(pk=new_pk)
                except Exception:
                    print(f"Skipping not existing report {new_pk}")
                    continue
                print(f"Processing report #{report.pk}")
                if report.xml:
                    # parse XML document
                    options = utils.parse_xml(report.xml)
                    for key, value in options.items():
                        if key == "tags":
                            report.tags.clear()
                            report.tags.add(*value)
                            report.modules = len(value)
                        else:
                            setattr(report, key, value)
                    report.save()
                elif report.json:
                    # parse JSON document
                    options = utils.parse_json(report.json)
                    # get installed modules
                    modules = utils.get_modules_from_json(report.json)
                    for key, value in options.items():
                        setattr(report, key, value)
                    if modules:
                        report.tags.clear()
                        report.tags.add(*modules)
                    report.modules = len(modules)
                    report.save()
