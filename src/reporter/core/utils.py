# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import connection
from django.utils.html import escape
from lxml import etree
from reporter.core import models
import os
import re


def parse_report_xml(xml):
    kwargs = {}
    root = etree.fromstring(xml)
    try:
        obspy_installed = root.xpath('/report/obspy/installed')[0].text
    except:
        obspy_installed = None
    try:
        core_installed = root.xpath('/report/obspy/core/installed')[0].text
    except:
        core_installed = None
    installed = obspy_installed or core_installed or None
    if installed and installed.startswith('0.0.0-'):
        installed = installed[6:]
    kwargs['installed'] = installed
    try:
        kwargs['timetaken'] = float(root.xpath('/report/timetaken')[0].text)
    except:
        kwargs['timetaken'] = None
    try:
        kwargs['skipped'] = int(root.xpath('/report/skipped')[0].text)
    except:
        kwargs['skipped'] = None
    try:
        kwargs['node'] = root.findtext('platform/node')
    except:
        kwargs['node'] = None
    return kwargs


def import_old_reports():
    """
    Imports reports from old SQLite database.
    """
    # import only if no report exist yet
    if models.Report.objects.count() > 0:
        print "Initial reports already imported ..."
        return
    else:
        print "Initial import of old reports ..."
    # parse old database
    import sqlite3
    c = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'reporter.db'))
    results = c.execute("""
        SELECT id, timestamp, tests, errors, failures, modules, system,
            architecture, version, xml, node
        FROM report""")
    # bulk create objects
    bulk = []
    for r in results:
        # parse XML
        kwargs = parse_report_xml(r[9])
        kwargs['node'] = r[10]
        # create report
        report = models.Report(id=r[0], datetime=datetime.fromtimestamp(r[1]),
            tests=r[2], errors=r[3], failures=r[4], modules=r[5], system=r[6],
            architecture=r[7], version=r[8], xml=r[9], **kwargs)
        print ' *', report
        bulk.append(report)
    models.Report.objects.bulk_create(bulk)
    # reset primary index
    # http://jesiah.net/post/23173834683/postgresql-primary-key-syncing-issues
    cursor = connection.cursor()
    cursor.execute("SELECT setval('core_report_id_seq', \
        (SELECT MAX(id) FROM core_report)+1)")
    print 'Initial import finished ...'


def set_default_selected_nodes():
    """
    Imports reports from old SQLite database.
    """
    # import only if no report exist yet
    if models.SelectedNode.objects.count() > 0:
        print "Initial selected nodes already imported ..."
        return
    else:
        print "Creating some selected nodes ..."
    # create default nodes
    for name in ['travis-ci', 'sphinx']:
        obj = models.SelectedNode(name=name)
        obj.save()
        print ' *', obj
    print 'Selected nodes have been created ...'


def format_traceback(text, tree=None):
    """
    Links directly to source files in tracebacks

    Credits for regexp magic: Tobias Megies (@megies)
    """
    if tree is None:
        tree = "master"
        linelink = ""
    else:
        linelink = r'#L\5'
    text = escape(unicode(text).encode("utf-8"))
    regex = r'(File &quot;)(.*[/\\](obspy[/\\][^&]*))(&quot;, line ([0-9]+),)'
    regex = re.compile(regex, re.UNICODE)
    regex_sub = r'\1<a href="https://github.com/obspy/obspy/blob/' + \
        r'%s/\3%s">\2</a>\4' % (tree, linelink)
    return regex.sub(regex_sub, text)
