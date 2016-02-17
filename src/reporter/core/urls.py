# -*- coding: utf-8 -*-

from django.conf.urls import url

import reporter.core.views


urlpatterns = [
    url(r'^$',
        view=reporter.core.views.index,
        name='index'),
    url(r'^home/$',
        view=reporter.core.views.home,
        name='home'),
    url(r'^(?P<pk>\d+)/xml/$',
        view=reporter.core.views.report_xml,
        name='report_xml'),
    url(r'^(?P<pk>\d+)/$',
        view=reporter.core.views.report_html,
        name='report_html'),
    url(r'^latest/$',
        view=reporter.core.views.report_latest,
        name='report_latest'),
    url(r'^rss/$',
        view=reporter.core.views.report_rss,
        name='report_rss'),
    url(r'^rss/(?P<name>[\w-]+)/$',
        view=reporter.core.views.report_rss_selectednode,
        name='report_rss_selectednode'),
    url(r'^snippets/navbar.html$',
        view=reporter.core.views.snippet_navbar,
        name='snippet_navbar'),
    url(r'^snippets/footer.html$',
        view=reporter.core.views.snippet_footer,
        name='snippet_footer'),
]
