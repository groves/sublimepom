import nav
import pom
from nose.tools import eq_


def test_standalonelib():
    parsed = pom.parse('test/javaproject/live/base/pom.xml')
    eq_(['jproj.base.Main'], list(nav.get_classes(parsed, test=True)))

def test_root_addition():
    lookup = nav.Lookup()
    lookup.addroots(['test/javaproject']).wait(1)
    eq_(['jproj.base.Main'], lookup.getclassesforpath('test/javaproject/live/base/src/main/java/jproj/base/Main.java'))
