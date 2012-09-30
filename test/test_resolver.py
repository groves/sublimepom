import maven
from nose.tools import eq_


def createreso():
    reso = maven.Resolver()
    for fn in maven.findpoms("test/goodpoms"):
        reso.addfile(fn)
    return reso


def test_transitive():
    reso = createreso()
    resolved = reso[('org.codehaus.mojo', 'transitivesimplestuser', '1.0', 'jar')]
    eq_("transitivesimplestuser", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "simplestuser", "1.0", "jar"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_parentdependenciesincluded():
    reso = createreso()
    resolved = reso[('org.codehaus.mojo', 'child', '1.0', 'jar')]
    eq_("child", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "setfields", "1.0", "swc"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])
