# -*- coding: utf-8 -*-

from django.db import models
import time


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
    installed = models.CharField(max_length=255, blank=True, null=True,
        db_index=True)
    node = models.CharField(max_length=64)
    system = models.CharField(max_length=16, db_index=True)
    architecture = models.CharField(max_length=16, db_index=True)
    version = models.CharField(max_length=16, db_index=True)
    xml = models.TextField(verbose_name='XML Document')

    def __unicode__(self):
        return "Report %d" % (self.pk)

    class Meta:
        ordering = ['-datetime']

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
                return "error"
            else:
                return "warning"
        else:
            return "success"

    @property
    def status_icon(self):
        if self.sum:
            if self.errors:
                return "icon-remove"
            else:
                return "icon-remove"
        else:
            return "icon-ok"

    @property
    def next_id(self):
        obj = self.get_next_by_datetime()
        if obj:
            return obj.id
        return False

    @property
    def previous_id(self):
        obj = self.get_previous_by_datetime()
        if obj:
            return obj.id
        return False

    @property
    def is_git(self):
        if self.installed.endswith('-dirty'):
            return False
        if '-g' in self.installed:
            # GIT
            return True
        if '.dev-r' in self.installed:
            # SVN
            return False
        if self.installed.startswith('0.5.'):
            return False
        if self.installed.startswith('0.6.'):
            return False
        if self.installed.startswith('0.7.'):
            return False
        if self.installed.count('.') == 2:
            return True
        return False


class SelectedNode(models.Model):
    """
    A pre-selected node.
    """
    name = models.CharField(max_length=64, primary_key=True)

    def __unicode__(self):
        return "SelectedNode %s" % (self.name)

    class Meta:
        ordering = ['name']
