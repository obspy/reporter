from django.conf import settings
from django.urls import include, path

from . import views


urlpatterns = [
    path(
        "",
        view=views.report_index,
        name="report_index",
    ),
    path(
        "<int:pk>/json/",
        view=views.report_json,
        name="report_json",
    ),
    path(
        "<int:pk>/xml/",  # deprecated
        view=views.report_xml,
        name="report_xml",
    ),
    path(
        "<int:pk>/",
        view=views.report_html,
        name="report_html",
    ),
    path(
        "post/v2/",
        view=views.report_post_v2,
        name="report_post_v2",
    ),
    path(
        "post/v1/",  # deprecated
        view=views.report_post_v1,
        name="report_post_v1",
    ),
    path(
        "latest/",
        view=views.report_latest,
        name="report_latest",
    ),
    path(
        "rss/",
        view=views.LatestReportsFeed(),
        name="report_rss",
    ),
    path(
        "rss/<slug:name>/",
        view=views.SelectedNodeReportsFeed(),
        name="report_rss_selectednode",
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
