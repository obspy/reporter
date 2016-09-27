# -*- coding: utf-8 -*-

import re
import urllib2

from django.utils.html import escape
from lxml import etree


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
    # GitHub pull request URL
    if root.find('prurl') is not None:
        kwargs['prurl'] = root.find('prurl').text
    else:
        kwargs['prurl'] = None
    # Continous Integration URL
    if root.find('ciurl') is not None:
        kwargs['ciurl'] = root.find('ciurl').text
    else:
        kwargs['ciurl'] = None
    # installed modules
    if root.find('obspy') is not None:
        kwargs['tags'] = sorted(
            [c.tag for c in root.find('obspy').getchildren()
             if c.tag != 'installed' and c.find('tested') is not None])
    else:
        kwargs['tags'] = []
    return kwargs


def replace_backslashes(match):
    """
    Replaces single backslashes with single forward slashes.
    Takes re match object as input (_sre.SRE_Match)
    """
    return match.group().replace('\\', '/')


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
    # extract imgur images
    imgurs = re.findall('http://i.imgur.com/[\w]*.png', text)
    # linkify
    regex = r'(File &quot;)(.*[/\\](obspy[/\\][^&]*))(&quot;, line ([0-9]+),)'
    regex = re.compile(regex, re.UNICODE)
    regex_sub = r'\1<a href="https://github.com/obspy/obspy/blob/' + \
        r'%s/\3%s">\2</a>\4' % (tree, linelink)
    text = regex.sub(regex_sub, text)
    # replace backslashes in href links
    regex = r'<a href="http.*?\.*?>'
    text = re.sub(regex, replace_backslashes, text)
    # make hyperlinks clickable
    regex = r'(http://\S*)'
    regex = re.compile(regex, re.UNICODE)
    regex_sub = r'<a href="\1">\1</a>'
    text = regex.sub(regex_sub, text)
    return text, imgurs


def fetch_credits():
    contributors = urllib2.urlopen(
        'https://raw.githubusercontent.com/obspy/'
        'obspy/master/obspy/CONTRIBUTORS.txt').read()
    funds = urllib2.urlopen(
        'https://raw.githubusercontent.com/obspy/'
        'obspy/master/misc/docs/source/credits/FUNDS.txt').read()
    # sort and split
    contributors = sorted(contributors.splitlines())
    funds = funds.splitlines()
    contributors = (contributors[0::2], contributors[1::2])
    return contributors, funds
