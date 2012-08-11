import pom
from nose.tools import eq_


def createrepo(*artifactIds):
    repo = pom.Repository()
    for artifactId in artifactIds:
        repo.addpom("test/goodpoms/%s.xml" % artifactId)
    return repo


def test_transitive():
    repo = createrepo("simplest", "simplestuser", "transitivesimplestuser")
    resolved = repo["test/goodpoms/transitivesimplestuser.xml"]
    eq_("transitivesimplestuser", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(pom.Coordinate("org.codehaus.mojo", "simplestuser", "1.0", "jar"),
        resolved.dependencies.keys()[0])
    eq_(pom.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])


def test_parentdependenciesincluded():
    repo = createrepo("parent", "child", "setfields", "simplest")
    resolved = repo["test/goodpoms/child.xml"]
    eq_("child", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(pom.Coordinate("org.codehaus.mojo", "setfields", "1.0", "swc"),
        resolved.dependencies.keys()[0])
    eq_(pom.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])
