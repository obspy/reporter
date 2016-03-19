# -*- coding: utf-8 -*-

import time

from django.db import models
from django.db.models import signals
from mptt.models import MPTTModel, TreeForeignKey


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
    prurl = models.URLField(verbose_name="Pull request URL", blank=True,
        null=True)
    ciurl = models.URLField(verbose_name="Continous Integration URL",
        blank=True, null=True)
    architecture = models.CharField(max_length=16, db_index=True)
    xml = models.TextField(verbose_name='XML Document')

    def __unicode__(self):
        return "Report %d" % (self.pk)

    class Meta:
        ordering = ['-datetime']

    @property
    def executed_tests(self):
        if self.skipped:
            return self.tests - self.skipped
        return self.tests

    @property
    def ciurl_type(self):
        if 'travis' in self.ciurl:
            return 'Tra'
        elif 'appveyor' in self.ciurl:
            return 'Apv'
        return None

    @property
    def prurl_number(self):
        try:
            return int(self.prurl.split('/')[-1])
        except:
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
            else:
                return "warning"
        else:
            return "success"

    @property
    def status_icon(self):
        if self.sum:
            if self.errors:
                return "glyphicon glyphicon-remove"
            else:
                return "glyphicon glyphicon-remove"
        else:
            return "glyphicon glyphicon-ok"

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
        if not self.installed:
            return False
        # new style dev version (see obspy/obspy#955)
        # e.g. 0.9.2.dev0+2003.g1b283f1b40.dirty.qulogic.pep440
        if '.dev0+' in self.installed:
            local_version = self.installed.split("+")[1].split(".")
            if len(local_version) > 1 and local_version[1].startswith("g"):
                if len(local_version[1]) != 11:
                    return False
                return True
            else:
                return False
        elif '0.0.0+archive' in self.installed:
            return False
        # old style dev version
        else:
            if self.installed is None:
                return False
            elif self.installed.endswith('-dirty'):
                return False
            elif '-g' in self.installed:
                # GIT
                return True
            elif '.dev-r' in self.installed:
                # SVN
                return False
            elif self.installed.startswith('0.5.'):
                return False
            elif self.installed.startswith('0.6.'):
                return False
            elif self.installed.startswith('0.7.'):
                return False
            elif self.installed.count('.') == 2:
                return True
        return False

    @property
    def git_commit_hash(self):
        if self.is_git:
            if '.dev0+' in self.installed:
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

    def __unicode__(self):
        return "SelectedNode %s" % (self.name)

    class Meta:
        ordering = ['name']


class MenuItem(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')
    name = models.CharField(max_length=50, help_text='Use "-" for dividers')
    icon = models.CharField(max_length=100, blank=True, null=True,
        help_text="see http://getbootstrap.com/components/#glyphicons-glyphs")
    url = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return "%s" % (self.name)

    def move_to(self, *args, **kwargs):
        # manually submit post_save signal on node move
        signals.post_save.send(sender=MenuItem, instance=self, created=False)
        return super(MenuItem, self).move_to(*args, **kwargs)
