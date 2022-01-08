from django.conf import settings
from django.urls import include, path

from . import views


urlpatterns = [
    path(
        "",
        view=views.index,
        name="index",
    ),
    path(
        "<pk>/xml/",
        view=views.report_xml,
        name="report_xml",
    ),
    path(
        "<int:pk>/",
        view=views.report_html,
        name="report_html",
    ),
    path(
        "latest/",
        view=views.report_latest,
        name="report_latest",
    ),
    path(
        "rss/",
        view=views.report_rss,
        name="report_rss",
    ),
    path(
        "rss/<slug:name>/",
        view=views.report_rss_selectednode,
        name="report_rss_selectednode",
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
