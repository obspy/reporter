from django.conf import settings
from django.urls import include, path

from . import views


urlpatterns = [
    path(
        "",
        view=views.core_index,
        name="core_index",
    ),
    path(
        "<int:pk>/json/",
        view=views.core_json,
        name="core_json",
    ),
    path(
        "<int:pk>/xml/",
        view=views.core_xml,
        name="core_xml",
    ),
    path(
        "<int:pk>/",
        view=views.core_html,
        name="core_html",
    ),
    # path(
    #     "report/1.0/",
    #     view=views.core_report,
    #     name="core_report",
    # ),
    path(
        "latest/",
        view=views.core_latest,
        name="core_latest",
    ),
    path(
        "rss/",
        view=views.LatestReportsFeed(),
        name="core_rss",
    ),
    path(
        "rss/<slug:name>/",
        view=views.SelectedNodeReportsFeed(),
        name="core_rss_selectednode",
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
