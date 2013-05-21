# -*- coding: utf-8 -*-

from django.test import TestCase
from reporter.core.utils import format_traceback


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
  File "d:\obspy\obspy\taup\tests\test_taup.py", line 26, \
in test_getTravelTimesAK135
    tt = getTravelTimes(delta=52.474, depth=611.0, model='ak135')
  File "d:\obspy\obspy\taup\taup.py", line 72, in getTravelTimes
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
        self.assertEqual(format_traceback(TB_SOURCE_1), TB_RESULT_1)
        self.assertEqual(format_traceback(TB_SOURCE_2), TB_RESULT_2)
