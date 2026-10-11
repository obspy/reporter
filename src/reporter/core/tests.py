import json
import time

from django.template import Context
from django.test import RequestFactory, TestCase

from . import models, utils, views
from .templatetags.append_to_get import AppendGetNode

TB_SOURCE_1 = """
Traceback (most recent call last):
  File "/testrun/git/obspy/core/tests/test_quakeml.py", line 516, in test_enums
    for stype in root.findall("xs:simpleType", namespaces=root.ns):
TypeError: findall() takes no keyword arguments
"""

TB_RESULT_1 = """
Traceback (most recent call last):
  File &quot;<a href="https://github.com/obspy/obspy/blob/master/obspy/core/\
tests/test_quakeml.py">/testrun/git/obspy/core/tests/test_quakeml.py</a>&quot;\
, line 516, in test_enums
    for stype in root.findall(&quot;xs:simpleType&quot;, namespaces=root.ns):
TypeError: findall() takes no keyword arguments
"""

TB_SOURCE_2 = """
Traceback (most recent call last):
  File "d:\\obspy\\obspy\taup\tests\test_taup.py", line 26, \
in test_getTravelTimesAK135
    tt = getTravelTimes(delta=52.474, depth=611.0, model='ak135')
  File "d:\\obspy\\obspy\taup\taup.py", line 72, in getTravelTimes
    phase_names, tt, toang, dtdd, dtdh, dddp = libtau.ttimes(delta, depth,
NameError: global name 'libtau' is not defined
"""

TB_RESULT_2 = """
Traceback (most recent call last):
  File &quot;d:\\obspy\\obspy\taup\tests\test_taup.py&quot;, line 26, \
in test_getTravelTimesAK135
    tt = getTravelTimes(delta=52.474, depth=611.0, model=&#39;ak135&#39;)
  File &quot;d:\\obspy\\obspy\taup\taup.py&quot;, line 72, in getTravelTimes
    phase_names, tt, toang, dtdd, dtdh, dddp = libtau.ttimes(delta, depth,
NameError: global name &#39;libtau&#39; is not defined
"""


class ReporterTest(TestCase):
    def test_format_traceback(self):
        """
        Tests for format_traceback utility function
        """
        self.assertEqual(utils.format_traceback(TB_SOURCE_1), TB_RESULT_1)
        self.assertEqual(utils.format_traceback(TB_SOURCE_2), TB_RESULT_2)

    def test_format_traceback_escapes_tree(self):
        log, _ = utils.format_traceback(TB_SOURCE_1, tree='1.0-g"x')
        self.assertIn('blob/1.0-g&quot;x/obspy/core/tests/test_quakeml.py#L516"', log)

    def test_append_to_get_escapes_query(self):
        request = RequestFactory().get("/", {"q": 'a"b', "pyversion": "3.12.0+"})
        url = AppendGetNode("page=p").render(Context({"request": request, "p": 2}))
        self.assertEqual(url, "/?q=a%22b&amp;pyversion=3.12.0%2B&amp;page=2")

    def test_prurl_number_requires_http_url(self):
        report = models.Report(prurl="https://github.com/obspy/obspy/pull/123")
        self.assertEqual(report.prurl_number, 123)
        report.prurl = "ftp://example.org/pull/123"
        self.assertIsNone(report.prurl_number)

    def test_report_post_rejects_future_timestamp(self):
        data = {
            "created": time.time() + 24 * 60 * 60,
            "dependencies": {"pytest": "8.0"},
            "summary": {"total": 1},
            "platform_info": {},
        }
        request = RequestFactory().post(
            "/post/v2/", json.dumps(data), content_type="application/json"
        )
        response = views.report_post_v2(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"future", response.content)
