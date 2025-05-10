import time

from django.db import models
from django.urls.base import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager


class ReportManager(models.Manager):
    """
    Default queryset manager
    """

    def get_queryset(self):
        return super().get_queryset().prefetch_related("tags")


class Report(models.Model):
    """
    A test report.
    """

    datetime = models.DateTimeField(verbose_name="Date/Time")
    tests = models.IntegerField()
    errors = models.IntegerField()
    failures = models.IntegerField()
    skipped = models.IntegerField(blank=True, null=True)
    modules = models.IntegerField()
    timetaken = models.FloatField(blank=True, null=True)
    installed = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    node = models.CharField(max_length=64)
    system = models.CharField(max_length=16, db_index=True)
    architecture = models.CharField(max_length=16, db_index=True)
    version = models.CharField(max_length=16, db_index=True)
    prurl = models.URLField(
        verbose_name="Pull request URL", blank=True, null=True, db_index=True
    )
    architecture = models.CharField(max_length=16, db_index=True)
    xml = models.TextField(verbose_name="XML document", blank=True, null=True)
    json = models.JSONField(verbose_name="JSON document", blank=True, null=True)

    objects = ReportManager()
    tags = TaggableManager()

    def __str__(self):
        return f"Report {self.pk}"

    class Meta:
        ordering = ["-datetime"]

    def get_absolute_url(self):
        return reverse("report_html", kwargs={"pk": self.pk})

    @property
    def executed_tests(self):
        if self.skipped:
            return self.tests - self.skipped
        return self.tests

    @property
    def prurl_number(self):
        try:
            return int(self.prurl.split("/")[-1])
        except Exception:
            return None

    @property
    def timestamp(self):
        return int(time.mktime(self.datetime.timetuple()))

    @property
    def sum(self):
        return self.failures + self.errors

    @property
    def status(self):
        if self.sum:
            if self.errors:
                return "danger"
            return "warning"
        return "success"

    @property
    def status_icon(self):
        if self.sum:
            if self.errors:
                return "glyphicon glyphicon-remove"
            return "glyphicon glyphicon-remove"
        return "glyphicon glyphicon-ok"

    @property
    def next_id(self):
        """
        Get next report ID or False if not available
        """
        try:
            return Report.objects.filter(id__gt=self.id).order_by("id").first().id
        except Exception:
            return False

    @property
    def previous_id(self):
        """
        Get previous report ID or False if not available
        """
        try:
            return Report.objects.filter(id__lt=self.id).order_by("-id").first().id
        except Exception:
            return False

    @property
    def is_git(self):
        if not self.installed:
            return False
        # new style dev version (see obspy/obspy#955)
        # e.g. 0.9.2.dev0+2003.g1b283f1b40.dirty.qulogic.pep440
        # n.b.: since obspy/obspy#1338 we have ".post0" instead of ".dev0"
        if ".dev0+" in self.installed or ".post0+" in self.installed:
            local_version = self.installed.split("+")[1].split(".")
            if len(local_version) > 1 and local_version[1].startswith("g"):
                if len(local_version[1]) != 11:
                    return False
                return True
            return False
        if "0.0.0+archive" in self.installed:
            return False
        # old style dev version
        if self.installed is None:
            return False
        if self.installed.endswith("-dirty"):
            return False
        if "-g" in self.installed:
            # GIT
            return True
        if ".dev-r" in self.installed:
            # SVN
            return False
        if self.installed.startswith("0.5."):
            return False
        if self.installed.startswith("0.6."):
            return False
        if self.installed.startswith("0.7."):
            return False
        if self.installed.count(".") == 2:
            return True
        return False

    @property
    def git_commit_hash(self):
        if self.is_git:
            if ".dev0+" in self.installed or ".post0+" in self.installed:
                local_version = self.installed.split("+")[1].split(".")
                if len(local_version) > 1 and local_version[1].startswith("g"):
                    return local_version[1][1:]
            return self.installed
        return None


class SelectedNode(models.Model):
    """
    A pre-selected node.
    """

    name = models.CharField(max_length=64, primary_key=True)

    def __str__(self):
        return f"SelectedNode {self.name}"

    class Meta:
        ordering = ["name"]


class MenuItem(MPTTModel):
    parent = TreeForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50, help_text='Use "-" for dividers')
    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="see http://getbootstrap.com/components/#glyphicons-glyphs",
    )
    url = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
