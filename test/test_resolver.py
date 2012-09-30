import maven
from nose.tools import eq_, ok_


def createreso():
    reso = maven.Resolver()
    reso.adddir("test/goodpoms")
    return reso


def test_transitive():
    reso = createreso()
    resolved = reso["test/goodpoms/transitivesimplestuser.xml"]
    eq_("transitivesimplestuser", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "simplestuser", "1.0", "jar"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_parentdependenciesincluded():
    reso = createreso()
    resolved = reso["test/goodpoms/child.xml"]
    eq_("child", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "setfields", "1.0", "swc"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_removedir():
    reso = createreso()
    ok_(len(reso) > 0)
    reso.removedir('test/goodpoms')
    eq_(0, len(reso))
