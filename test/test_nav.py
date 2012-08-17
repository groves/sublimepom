import nav
import pom
from nose.tools import eq_


def test_standalonelib():
    parsed = pom.parse('test/javaproject/live/base/pom.xml')
    eq_(['jproj.base.Main'], list(nav.get_classes(parsed, test=True)))
