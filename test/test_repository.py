import maven
from nose.tools import eq_, ok_


def createrepo():
    repo = maven.Repository()
    repo.adddir("test/goodpoms")
    return repo


def test_transitive():
    repo = createrepo()
    resolved = repo["test/goodpoms/transitivesimplestuser.xml"]
    eq_("transitivesimplestuser", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "simplestuser", "1.0", "jar"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_parentdependenciesincluded():
    repo = createrepo()
    resolved = repo["test/goodpoms/child.xml"]
    eq_("child", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(maven.Coordinate("org.codehaus.mojo", "setfields", "1.0", "swc"),
        resolved.dependencies.keys()[0])
    eq_(maven.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_removedir():
    repo = createrepo()
    ok_(len(repo.poms_by_location) > 0)
    repo.removedir('test/goodpoms')
    eq_({}, repo.poms_by_location)
