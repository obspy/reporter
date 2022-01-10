import re
from urllib.request import urlopen

from django.conf import settings
from django.utils.html import escape
from lxml import etree


def get_module_from_nodeid(nodeid):
    nodeid = nodeid.split("::", 1)[0]
    nodeid = nodeid.split("/tests/", 1)[0]
    nodeid = nodeid.split("/scripts/", 1)[0]
    nodeid = nodeid.split("/__init__.py", 1)[0]
    nodeid = nodeid.replace("/", ".")
    if nodeid.startswith("obspy."):
        nodeid = nodeid[6:]
    return nodeid


def get_modules_from_json(data):
    try:
        modules = [
            get_module_from_nodeid(c["nodeid"])
            for c in data["collectors"]
            if c["nodeid"].startswith("obspy/")
            and c["nodeid"].endswith("/__init__.py")
            and 1 <= c["nodeid"].count("/") <= 3
            and c["result"] != []
        ]
    except Exception:
        modules = []
    # remove duplicates
    modules = list(dict.fromkeys(modules))
    # cleanup
    if "obspy" in modules:
        modules.remove("obspy")
    return modules


def parse_json(data):
    """
    Parse JSON document for additional information
    """
    kwargs = {}
    try:
        kwargs["installed"] = data["dependencies"]["obspy"]
        if kwargs["installed"].startswith("0.0.0-"):
            kwargs["installed"] = kwargs["installed"][6:]
    except Exception:
        kwargs["installed"] = None
    try:
        kwargs["timetaken"] = float(data["duration"])
    except Exception:
        kwargs["timetaken"] = None
    try:
        kwargs["skipped"] = int(data["summary"]["skipped"])
    except Exception:
        kwargs["skipped"] = None
    try:
        kwargs["node"] = data["platform_info"]["node"][:16]
    except Exception:
        kwargs["node"] = ""
    # GitHub pull request URL
    try:
        kwargs["prurl"] = data["ci_info"]["pr_url"]
    except Exception:
        kwargs["prurl"] = None
    return kwargs


def parse_xml(data):
    """
    Parse XML document for additional information (deprecated)
    """
    kwargs = {}
    root = etree.fromstring(data)
    try:
        obspy_installed = root.xpath("/report/obspy/installed")[0].text
    except Exception:
        obspy_installed = None
    try:
        core_installed = root.xpath("/report/obspy/core/installed")[0].text
    except Exception:
        core_installed = None
    installed = obspy_installed or core_installed or None
    if installed and installed.startswith("0.0.0-"):
        installed = installed[6:]
    kwargs["installed"] = installed
    try:
        kwargs["timetaken"] = float(root.xpath("/report/timetaken")[0].text)
    except Exception:
        kwargs["timetaken"] = None
    try:
        kwargs["skipped"] = int(root.xpath("/report/skipped")[0].text)
    except Exception:
        kwargs["skipped"] = None
    try:
        kwargs["node"] = root.findtext("platform/node")
    except Exception:
        kwargs["node"] = ""
    # GitHub pull request URL
    if root.find("prurl") is not None:
        kwargs["prurl"] = root.find("prurl").text
    else:
        kwargs["prurl"] = None
    # installed modules
    if root.find("obspy") is not None:
        kwargs["tags"] = sorted(
            [
                c.tag
                for c in root.find("obspy").getchildren()
                if c.tag != "installed" and c.find("tested") is not None
            ]
        )
    else:
        kwargs["tags"] = []
    return kwargs


def replace_backslashes(match):
    """
    Replaces single backslashes with single forward slashes.
    Takes re match object as input (_sre.SRE_Match)
    """
    return match.group().replace("\\", "/")


def format_traceback(text, tree=None):
    """
    Links directly to source files in tracebacks

    Credits for regexp magic: Tobias Megies (@megies)
    """
    if tree is None:
        tree = "master"
        linelink = ""
    else:
        linelink = r"#L\5"
    text = escape(text)
    # extract imgur images
    imgurs = re.findall(r"http://i.imgur.com/[\w]*.png", text)
    # ensure https links in imgur images
    imgurs = [i.replace("http://", "https://") for i in imgurs]
    # linkify
    regex = r"(File &quot;)(.*[/\\](obspy[/\\][^&]*))(&quot;, line ([0-9]+),)"
    regex = re.compile(regex)
    regex_sub = (
        rf'\1<a href="https://github.com/obspy/obspy/blob/{tree}/\3{linelink}">\2</a>\4'
    )
    text = regex.sub(regex_sub, text)
    # replace backslashes in href links
    regex = r'<a href="http.*?\.*?>'
    text = re.sub(regex, replace_backslashes, text)
    # make hyperlinks clickable
    regex = r"(http://\S*)"
    regex = re.compile(regex)
    regex_sub = r'<a href="\1">\1</a>'
    text = regex.sub(regex_sub, text)
    return text, imgurs


def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n)]


def fetch_credits():
    contributors = urlopen(
        "https://raw.githubusercontent.com/obspy/" "obspy/master/obspy/CONTRIBUTORS.txt"
    ).read()
    contributors = contributors.decode("utf-8")
    funds = urlopen(
        "https://raw.githubusercontent.com/obspy/"
        "obspy/master/misc/docs/source/credits/FUNDS.txt"
    ).read()
    funds = funds.decode("utf-8")
    # sort and split
    contributors = sorted(contributors.splitlines())
    funds = funds.splitlines()
    contributors = split(contributors, 4)
    return contributors, funds


def cache_page_if_not_latest(model, decorator):
    def _decorator(view):
        decorated_view = decorator(view)

        def _view(request, *args, **kwargs):
            # skip caching if in debug mode
            debug = settings.DEBUG
            if debug:
                return view(request, *args, **kwargs)
            # cache everything except very latest report
            cacheit = False
            try:
                pk = int(kwargs["pk"])
                if pk == model.objects.latest("id").id:
                    cacheit = False
                else:
                    cacheit = True
            except Exception:
                pass
            if cacheit:
                # view with @cache
                return decorated_view(request, *args, **kwargs)
            else:
                # view without @cache
                return view(request, *args, **kwargs)

        return _view

    return _decorator
