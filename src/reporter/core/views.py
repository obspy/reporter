import ast
import copy
import json
from datetime import datetime
from urllib.request import urlopen

from django.contrib.syndication.views import Feed
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http.response import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from lxml import etree

from reporter.core.utils import cache_page_if_not_latest

from . import models, utils

LIMITS = [50, 100, 200]


@require_http_methods(["POST"])
def report_post_v2(request):
    """
    Upload new report as JSON document - API version 2
    """
    if request.content_type != "application/json":
        return HttpResponseBadRequest("Wrong content type")

    # sanitize JSON data
    try:
        # parse POST parameters
        data = json.loads(utils.sanitize_json(request.body))
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    # check if pytest report
    try:
        assert data["dependencies"]["pytest"]
    except Exception:
        # old style pytest-metadata < 2.0
        try:
            assert data["environment"]["Packages"]["pytest"]
        except Exception:
            return HttpResponseBadRequest("Invalid report - missing pytest dependency")

    # required data
    try:
        tests = int(data["summary"].get("total", 0))
        errors = int(data["summary"].get("failed", 0)) + int(
            data["summary"].get("error", 0)
        )
        version = data["platform_info"].get("python_version", "")[:16]
        timestamp = float(data.get("created", 0))
        system = data["platform_info"].get("system", "")[:16]
        architecture = data["platform_info"].get("architecture")[:16]
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    # parse JSON document
    kwargs = utils.parse_json(data)
    # get installed modules
    modules = utils.get_modules_from_json(data)

    # create report
    report = models.Report(
        datetime=datetime.fromtimestamp(timestamp),
        tests=tests,
        errors=errors,
        failures=0,
        modules=len(modules),
        system=system,
        architecture=architecture,
        version=version,
        json=data,
        **kwargs,
    )
    report.save()
    # create tags
    if modules:
        report.tags.add(*modules)
    return JsonResponse(
        {"url": request.build_absolute_uri(reverse("report_html", args=(report.pk,)))}
    )


@require_http_methods(["POST"])
def report_post_v1(request):
    """
    Upload new report as XML document - API version 1 (deprecated)
    """
    # get headers
    try:
        # parse POST parameters
        data = request.POST.get("xml")
        tests = int(request.POST.get("tests"))
        errors = int(request.POST.get("errors"))
        failures = int(request.POST.get("failures"))
        version = request.POST.get("python_version")[:16]
        timestamp = int(request.POST.get("timestamp"))
        modules = int(request.POST.get("modules"))
        system = request.POST.get("system")[:16]
        architecture = request.POST.get("architecture")[:16]
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    # check if XML is parseable
    try:
        etree.fromstring(data)
    except Exception:
        # otherwise try to correct broken XML
        try:
            parser = etree.XMLParser(recover=True)
            data = etree.tostring(etree.fromstring(data, parser=parser))
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    # parse XML document
    kwargs = utils.parse_xml(data)
    if "tags" in kwargs:
        tags = kwargs.pop("tags")
    # create report
    report = models.Report(
        datetime=datetime.fromtimestamp(timestamp),
        tests=tests,
        errors=errors,
        failures=failures,
        modules=modules,
        system=system,
        architecture=architecture,
        version=version,
        xml=data,
        **kwargs,
    )
    report.save()
    # create tags
    if tags:
        report.tags.add(*tags)
    return JsonResponse(
        {"url": request.build_absolute_uri(reverse("report_html", args=(report.pk,)))}
    )


def report_index(request):
    """
    Displays start page with table of all recent test reports
    """
    # deprecated XML upload end point
    if request.method == "POST":
        return report_post_v1(request)

    # redirect old GET URLs
    if "id" in request.GET:
        try:
            return redirect("report_html", pk=request.GET.get("id"))
        except NoReverseMatch:
            pass
    elif "xml_id" in request.GET:
        try:
            return redirect("report_xml", pk=request.GET.get("xml_id"))
        except NoReverseMatch:
            pass

    # limits
    try:
        limit = int(request.GET.get("limit"))
        if limit not in LIMITS:
            raise
    except Exception:
        limit = LIMITS[0]

    queryset = models.Report.objects.all()

    # errors
    show = request.GET.get("show")
    if show == "errors":
        queryset = queryset.filter(Q(failures__gt=0) | Q(errors__gt=0))

    # filter by system
    systems = (
        models.Report.objects.values_list("system", flat=True)
        .distinct()
        .order_by("system")
    )
    try:
        system = request.GET.get("system")
        if system not in systems:
            raise
        queryset = queryset.filter(system=system)
    except Exception:
        system = None

    # filter by architecture
    architectures = (
        models.Report.objects.values_list("architecture", flat=True)
        .distinct()
        .order_by("architecture")
    )
    try:
        architecture = request.GET.get("architecture")
        if architecture not in architectures:
            raise
        queryset = queryset.filter(architecture=architecture)
    except Exception:
        architecture = None

    # filter by python version
    pyversions = (
        models.Report.objects.values_list("version", flat=True)
        .distinct()
        .order_by("-version")
    )
    try:
        pyversion = request.GET.get("pyversion")
        # plus sign gets replaced to space by browser
        pyversion = pyversion.replace(" ", "+")
        if pyversion not in pyversions:
            raise
        queryset = queryset.filter(version=pyversion)
    except Exception:
        pyversion = None

    # filter by ObsPy version
    try:
        version = request.GET.get("version") or None
        if version:
            queryset = queryset.filter(installed=version)
    except Exception:
        pass

    # filter by a git commit SHA in an untagged version
    try:
        git = request.GET.get("git") or None
        if git:
            # obspy version numbers contain only the first 10 characters of the
            # git commit SHA
            git = git[:10]
            queryset = queryset.filter(installed__contains=git)
    except Exception:
        pass

    # filter by node
    nodes = models.SelectedNode.objects.values_list("name", flat=True)
    try:
        node = request.GET.get("node") or None
        if node:
            queryset = queryset.filter(node__contains=node)
    except Exception:
        node = None

    # filter by PR number
    try:
        pr = request.GET.get("pr") or None
        if pr:
            queryset = queryset.filter(prurl__endswith="/" + pr)
    except Exception:
        pr = None

    # filter by module
    try:
        module = request.GET.get("module") or None
        if module:
            queryset = queryset.filter(tags__name__in=[module])
    except Exception:
        module = None

    # pagination
    paginator = Paginator(queryset, limit)
    page = request.GET.get("page")
    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    context = {
        "limit": limit,
        "limits": LIMITS,
        "reports": reports,
        "system": system,
        "systems": systems,
        "architecture": architecture,
        "architectures": architectures,
        "pyversion": pyversion,
        "pyversions": pyversions,
        "node": node,
        "nodes": nodes,
        "show": show,
    }
    return render(request, "index.html", context)


@cache_page_if_not_latest(model=models.Report, decorator=cache_page(60 * 60))
def report_html(request, pk):
    """
    Displays HTML overview page for given report
    """
    report = get_object_or_404(models.Report, pk=pk)
    if report.xml:
        return _report_html_xml(request, report)
    elif report.json:
        return _report_html_json(request, report)
    else:
        return Http404("Not implemented")


def _report_html_json(request, report):
    data = report.json
    git_hash = report.git_commit_hash
    tags = sorted(
        list(report.tags.values_list("name", flat=True)), key=len, reverse=True
    )
    # platform information
    platform = sorted(
        [
            (k.replace("_", " ").title(), v)
            for k, v in data.get("platform_info", {}).items()
        ]
    )
    # dependencies
    dependencies = sorted(
        [(k, v or "Not Installed") for k, v in data.get("dependencies", {}).items()]
    )
    # warnings
    warnings = data.get("warnings", {})
    # remove duplicates
    warnings = [dict(t) for t in {tuple(d.items()) for d in warnings}]
    # inspect tests and derive slowest test, skipped test, tracebacks etc.
    modules_dict = {}
    modules_dict_defaults = {
        "name": "",
        "tested": False,
        "status": "active",
        "tests": 0,
        "skipped": 0,
        "executed_tests": 0,
        "sum": 0,
        "tracebacks": [],
        "timetaken": 0,
    }
    for tag in sorted(tags):
        modules_dict[tag] = copy.deepcopy(modules_dict_defaults)
        modules_dict[tag]["name"] = f"obspy.{tag}"

    skipped_tests = []
    slowest_tests = []
    tracebacks = []

    for item in data["tests"]:
        nodeid = item["nodeid"]
        outcome = item["outcome"]
        filename = nodeid.split("::", 1)[0]
        lineno = item["lineno"]

        # get module using tags
        parts0 = filename.rsplit(".py", 1)[0].replace("/", ".")
        module = ""
        if parts0.startswith("obspy."):
            parts0 = parts0[6:]
        for tag in tags:
            if parts0.startswith(tag):
                module = tag
                break

        # create default entry for tests not in known default modules
        if not module:
            module = "other"
            if "other" not in modules_dict:
                modules_dict["other"] = copy.deepcopy(modules_dict_defaults)
                modules_dict["other"]["name"] = "other"

        # parse stages for duration and longrepr (traceback/reason)
        reason = ""
        traceback = ""
        duration = 0
        for key in ["call", "setup", "teardown"]:
            duration += item.get(key, {}).get("duration", 0)
            temp = item.get(key, {}).get("longrepr", "")
            if temp:
                if outcome == "skipped":
                    reason += ast.literal_eval(temp)[2]
                elif outcome in ["failed", "error"]:
                    traceback += temp

        modules_dict[module]["timetaken"] += duration
        modules_dict[module]["tests"] += 1

        # handle tests by outcome
        if outcome == "skipped":
            # skipped tests
            skipped_tests.append(
                (
                    module,
                    nodeid,
                    reason,
                    filename,
                    lineno,
                )
            )
            modules_dict[module]["skipped"] += 1
        elif outcome == "passed":
            # passed test -> handle slowest test
            slowest_tests.append(
                (
                    duration,
                    nodeid,
                    filename,
                    lineno,
                )
            )
            modules_dict[module]["tested"] = True
            if modules_dict[module]["status"] not in ["danger", "warning"]:
                modules_dict[module]["status"] = "success"
            modules_dict[module]["executed_tests"] += 1
        elif outcome in ["failed", "error"]:
            # failed test -> handle tracebacks
            tb = {}
            tb["module"] = module
            tb["id"] = len(tracebacks) + 1
            tb["log"], tb["imgurs"] = utils.format_traceback(traceback, git_hash)
            tb["imgurs"] = None
            if "network" in item.get("keywords", []):
                tb["status"] = "warning"
            else:
                tb["status"] = "danger"
            tracebacks.append(tb)
            # add to modules dict
            modules_dict[module]["tracebacks"].append(tb)
            modules_dict[module]["tested"] = True
            if modules_dict[module]["status"] != "danger":
                # set only if not already highest level
                modules_dict[module]["status"] = tb["status"]
            modules_dict[module]["executed_tests"] += 1
            modules_dict[module]["sum"] += 1
    # cleanup
    slowest_tests = sorted(slowest_tests, reverse=True)[0:20]
    modules = modules_dict.values()
    # api.icndb.com
    url = "http://api.icndb.com/jokes/random?limitTo=[nerdy]&escape=javascript"
    try:
        full_json = urlopen(url).read()
        full = json.loads(full_json)
        icndb = full["value"]["joke"]
    except Exception:
        icndb = None
    # render page
    context = {
        "report": report,
        "one_version": True,
        "platform": platform,
        "dependencies": dependencies,
        "modules": modules,
        "tracebacks": tracebacks,
        "slowest_tests": slowest_tests,
        "skipped_tests": skipped_tests,
        "warnings": warnings,
        "icndb": icndb,
    }
    return render(request, "report.html", context)


def _report_html_xml(request, report):
    # check if XML is parseable
    root = etree.fromstring(report.xml)
    # platform information
    if root.find("platform") is not None:
        platform = sorted(
            [
                (i.tag.replace("_", " ").title(), i.text)
                for i in root.find("platform").getchildren()
            ]
        )
    else:
        platform = []
    # dependencies
    if root.find("dependencies") is not None:
        dependencies = sorted(
            [
                (i.tag, i.text or "Not Installed")
                for i in root.find("dependencies").getchildren()
            ]
        )
    else:
        dependencies = []
    # skipped tests
    if root.find("skipped_tests_details") is not None:
        # Safely evaluate a string containing a Python expression
        skipped_tests = ast.literal_eval(root.find("skipped_tests_details").text)
    else:
        skipped_tests = []
    # slowest tests
    if root.find("slowest_tests") is not None:
        # Safely evaluate a string containing a Python expression
        slowest_tests = ast.literal_eval(root.find("slowest_tests").text)
    else:
        slowest_tests = []
    # modules
    if root.find("obspy") is not None:
        temp = sorted(
            [
                (c.tag, c)
                for c in root.find("obspy").getchildren()
                if c.tag != "installed"
            ]
        )
    else:
        temp = []
    modules = []
    tracebacks = []
    one_version = True
    git_hash = report.git_commit_hash
    for key, item in temp:
        obj = {}
        obj["name"] = f"obspy.{key}"
        version = item.findtext("installed")
        if version:
            if version.startswith("0.0.0-"):
                version = version[6:]
            if version != report.installed:
                one_version = False
        obj["version"] = version
        obj["tested"] = False
        tested = item.find("tested")
        if tested is not None:
            obj["status"] = "success"
            module_tracebacks = []
            # timetaken
            try:
                timetaken = float(item.findtext("timetaken"))
            except Exception:
                timetaken = None
            # failures
            if item.find("failures") is not None:
                failures = item.find("failures").getchildren()
                for error in failures:
                    tb = {}
                    tb["module"] = obj["name"]
                    tb["id"] = len(tracebacks) + 1
                    tb["log"], tb["imgurs"] = utils.format_traceback(
                        error.text, git_hash
                    )
                    tb["status"] = "warning"
                    module_tracebacks.append(tb)
                    tracebacks.append(tb)
                    obj["status"] = tb["status"]
            else:
                failures = []
            # errors
            if item.find("errors") is not None:
                errors = item.find("errors").getchildren()
                for error in errors:
                    tb = {}
                    tb["module"] = obj["name"]
                    tb["id"] = len(tracebacks) + 1
                    tb["log"], tb["imgurs"] = utils.format_traceback(
                        error.text, git_hash
                    )
                    tb["status"] = "danger"
                    module_tracebacks.append(tb)
                    tracebacks.append(tb)
                    obj["status"] = tb["status"]
            else:
                errors = []
            obj["tested"] = True
            obj["tests"] = int(item.findtext("tests"))
            try:
                obj["skipped"] = int(item.findtext("skipped"))
                obj["executed_tests"] = obj["tests"] - obj["skipped"]
            except Exception:
                obj["skipped"] = ""
                obj["executed_tests"] = obj["tests"]
            obj["sum"] = len(errors) + len(failures)
            obj["tracebacks"] = module_tracebacks
            obj["timetaken"] = timetaken
        else:
            obj["status"] = "active"
        modules.append(obj)
    # install log
    try:
        log = root.findtext("install_log")
        if not log:
            raise
        log = str(log)
    except Exception:
        log = None
    # api.icndb.com
    url = "http://api.icndb.com/jokes/random?limitTo=[nerdy]&escape=javascript"
    try:
        full_json = urlopen(url).read()
        full = json.loads(full_json)
        icndb = full["value"]["joke"]
    except Exception:
        icndb = None
    # render page
    context = {
        "report": report,
        "one_version": one_version,
        "platform": platform,
        "dependencies": dependencies,
        "modules": modules,
        "tracebacks": tracebacks,
        "log": log,
        "slowest_tests": slowest_tests,
        "skipped_tests": skipped_tests,
        "icndb": icndb,
    }
    return render(request, "report.html", context)


class LatestReportsFeed(Feed):
    """
    RSS feed for latest test reports
    """

    title = "ObsPy Reporter"
    link = "/rss/"
    description = "Latest failing test reports on tests.obspy.org."

    def items(self):
        return models.Report.objects.filter(
            Q(failures__gt=0) | Q(errors__gt=0)
        ).order_by("-datetime")[:20]

    def item_title(self, report):
        context = {"report": report}
        return get_template("rss_title.html").render(context)

    def item_description(self, report):
        context = {"report": report}
        return get_template("rss.html").render(context)

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse("report_html", args=[item.pk])


class SelectedNodeReportsFeed(Feed):
    """
    RSS feed for latest test reports filtered by selected node
    """

    description = "Latest updates on tests.obspy.org"

    def get_object(self, request, name):
        return get_object_or_404(models.SelectedNode, name=name)

    def title(self, node):
        return f"ObsPy Reporter ({node.name})"

    def link(self, node):
        return reverse("report_rss_selectednode", args=[node.name])

    def description(self, node):
        return f"Latest failing test reports on tests.obspy.org for node {node.name}"

    def items(self, node):
        return (
            models.Report.objects.filter(Q(failures__gt=0) | Q(errors__gt=0))
            .filter(node=node.name)
            .order_by("-datetime")[:20]
        )

    def item_title(self, report):
        context = {"report": report}
        return get_template("rss_title.html").render(context)

    def item_description(self, report):
        context = {"report": report}
        return get_template("rss.html").render(context)

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse("report_html", args=[item.pk])


@cache_page(60 * 60 * 24 * 7)
def report_xml(request, pk):
    """
    Returns XML document of given report (deprecated)
    """
    report = get_object_or_404(models.Report, pk=pk)
    xml_doc = report.xml
    if not xml_doc.startswith("<?xml"):
        xml_doc = '<?xml version="1.0" encoding="UTF-8"?>' + xml_doc
    return HttpResponse(xml_doc, content_type="text/xml")


@cache_page(60 * 60 * 24 * 7)
def report_json(request, pk):
    """
    Returns JSON document of given report
    """
    report = get_object_or_404(models.Report, pk=pk)
    json_doc = report.json
    return JsonResponse(json_doc)


def report_latest(request):
    """
    Redirect to latest report
    """
    obj = models.Report.objects.latest("datetime")
    return redirect("report_html", pk=obj.id)
