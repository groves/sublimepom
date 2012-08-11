import os
import pom
from nose.tools import eq_, raises


def testbadpoms():
    for path in os.listdir('test/badpoms'):
        yield checkbadpom, 'test/badpoms/' + path


@raises(pom.MalformedPomException)
def checkbadpom(path):
    pom.parse(path)


def testsimplepom():
    checkgoodpom('test/goodpoms/simplest.xml')


def testchildpom():
    p = checkgoodpom('test/goodpoms/child.xml', artifact="my-subproject")
    eq_(len(p._dependencies), 2)
    otherproj = p._dependencies[0]
    eq_("org.codehaus.mojo", otherproj._group)
    eq_("1.0", otherproj._version)
    eq_("my-otherproject", otherproj._artifact)
    eq_("compile", otherproj._scope)
    eq_("jar", otherproj._packaging)
    eq_("false", otherproj._optional)

    otherprojswf = p._dependencies[1]
    eq_("org.codehaus.mojo", otherprojswf._group)
    eq_("1.0", otherprojswf._version)
    eq_("my-otherproject", otherprojswf._artifact)
    eq_("test", otherprojswf._scope)
    eq_("swf", otherprojswf._packaging)
    eq_("true", otherprojswf._optional)


def testsetfields():
    checkgoodpom('test/goodpoms/setfields.xml', packaging="swc")


def checkgoodpom(path, group="org.codehaus.mojo", artifact="my-project", version="1.0", packaging="jar"):
    p = pom.parse(path)
    eq_(group, p._group)
    eq_(artifact, p._artifact)
    eq_(version, p._version)
    eq_(packaging, p._packaging)
    return p
