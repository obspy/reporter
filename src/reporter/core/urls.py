# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url
from django.urls import include, path

from . import views


urlpatterns = [
    url(r'^$',
        view=views.index,
        name='index'),
    url(r'^(?P<pk>\d+)/xml/$',
        view=views.report_xml,
        name='report_xml'),
    url(r'^(?P<pk>\d+)/$',
        view=views.report_html,
        name='report_html'),
    url(r'^latest/$',
        view=views.report_latest,
        name='report_latest'),
    url(r'^rss/$',
        view=views.report_rss,
        name='report_rss'),
    url(r'^rss/(?P<name>[\w-]+)/$',
        view=views.report_rss_selectednode,
        name='report_rss_selectednode'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
