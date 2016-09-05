# -*- coding: utf-8 -*-

from django.conf.urls import url

import reporter.core.views


urlpatterns = [
    url(r'^$',
        view=reporter.core.views.home,
        name='home'),
    url(r'^tests/$',
        view=reporter.core.views.index,
        name='index'),
    url(r'^tests/(?P<pk>\d+)/xml/$',
        view=reporter.core.views.report_xml,
        name='report_xml'),
    url(r'^tests/(?P<pk>\d+)/$',
        view=reporter.core.views.report_html,
        name='report_html'),
    url(r'^tests/latest/$',
        view=reporter.core.views.report_latest,
        name='report_latest'),
    url(r'^tests/rss/$',
        view=reporter.core.views.report_rss,
        name='report_rss'),
    url(r'^tests/rss/(?P<name>[\w-]+)/$',
        view=reporter.core.views.report_rss_selectednode,
        name='report_rss_selectednode'),
    url(r'^snippets/navbar.html$',
        view=reporter.core.views.snippet_navbar,
        name='snippet_navbar'),
    url(r'^snippets/footer.html$',
        view=reporter.core.views.snippet_footer,
        name='snippet_footer'),
]
