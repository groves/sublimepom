import pom
from nose.tools import eq_


def test_transitive():
    repo = pom.Repository()
    for artifactId in ["simplest", "simplestuser", "transitivesimplestuser"]:
        repo.addpom("test/goodpoms/%s.xml" % artifactId)
    resolved = repo["test/goodpoms/transitivesimplestuser.xml"]
    eq_("transitivesimplestuser", resolved._artifactId)
    eq_(2, len(resolved.dependencies))

    eq_(pom.Coordinate("org.codehaus.mojo", "simplestuser", "1.0", "jar"),
        resolved.dependencies.keys()[0])
    eq_(pom.Coordinate("org.codehaus.mojo", "simplest", "1.0", "jar"),
        resolved.dependencies.keys()[1])
