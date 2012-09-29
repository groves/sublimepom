import nav
import os
import pom
from nose.tools import eq_


def test_standalonelib():
    parsed = pom.parse('test/javaproject/live/base/pom.xml')
    classlocs = list(nav.get_classes(parsed, test=True))
    eq_(1, len(classlocs))
    eq_('jproj.base.Main', classlocs[0].classname)
    eq_(os.path.abspath('test/javaproject/live/base/src/main/java/jproj/base/Main.java'), classlocs[0].path)

def test_root_addition():
    lookup = nav.Lookup()
    lookup.addroots(['test/javaproject']).wait(1)
    classlocs = list(lookup.getclassesforpath('test/javaproject/live/base/src/main/java/jproj/base/Main.java'))
    eq_(1, len(classlocs))
    eq_('jproj.base.Main', classlocs[0].classname)
    eq_(os.path.abspath('test/javaproject/live/base/src/main/java/jproj/base/Main.java'), classlocs[0].path)
