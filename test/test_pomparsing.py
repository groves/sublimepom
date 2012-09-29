import os
import maven
from nose.tools import eq_, raises


def testbadpoms():
    for path in os.listdir('test/badpoms'):
        yield checkbadpom, 'test/badpoms/' + path


@raises(maven.MalformedPomException)
def checkbadpom(path):
    maven.parse(path)


def testsimplepom():
    checkgoodpom('test/goodpoms/simplest.xml')


def testchildpom():
    p = checkgoodpom('test/goodpoms/child.xml', artifact="child")
    eq_(len(p._dependencies), 1)

    setfields = p._dependencies[0]
    eq_("${project.groupId}", setfields._groupId)
    eq_("${codehaus.mojo.version}", setfields._version)
    eq_("${child.setfields.artifactId}", setfields._artifactId)
    eq_("test", setfields._scope)
    eq_("swc", setfields._packaging)
    eq_("true", setfields._optional)


def testsetfields():
    checkgoodpom('test/goodpoms/setfields.xml', artifact="setfields", packaging="swc")


def checkgoodpom(path, group="org.codehaus.mojo", artifact="simplest", version="1.0", packaging="jar"):
    p = maven.parse(path)
    eq_(group, p._groupId)
    eq_(artifact, p._artifactId)
    eq_(version, p._version)
    eq_(packaging, p._packaging)
    return p
