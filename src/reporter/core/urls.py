# -*- coding: utf-8 -*-

from django.conf.urls import url

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
    url(r'^snippets/navbar.html$',
        view=views.snippet_navbar,
        name='snippet_navbar'),
    url(r'^snippets/footer.html$',
        view=views.snippet_footer,
        name='snippet_footer'),
]
