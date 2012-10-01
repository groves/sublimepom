import maven
from nose.tools import eq_


def createreso(base="test/goodpoms/basic"):
    reso = maven.Resolver()
    for fn in maven.findpoms(base):
        reso.addpom(maven.parse(fn))
    return reso

def test_transitive():
    reso = createreso()
    resolved = reso[('org.codehaus.mojo', 'transitivesimplestuser', 'jar', '1.0')]
    eq_("transitivesimplestuser", resolved._artifactId)

    eq_([("org.codehaus.mojo", "simplestuser", "jar", "1.0"), ("org.codehaus.mojo", "simplest", "jar", "1.0")],
        [dep.versioned for dep in resolved.dependencies.values()])


def test_parentdependenciesincluded():
    reso = createreso()
    resolved = reso[('org.codehaus.mojo', 'child', 'jar', '1.0')]
    eq_("child", resolved._artifactId)

    eq_([("org.codehaus.mojo", "setfields", "swc", "1.0"), ("org.codehaus.mojo", "simplest", "jar", "1.0")],
        [dep.versioned for dep in resolved.dependencies.values()])

def test_updatedep():
    reso = createreso()
    resolved = reso[('org.codehaus.mojo', 'setfields', 'swc', '1.0')]
    initialdepcount = len(reso)
    eq_(0, len(resolved.dependencies))

    reso.addpom(maven.parse('test/goodpoms/setfields_with_dep.xml'))
    resolved = reso[('org.codehaus.mojo', 'setfields', 'swc', '1.0')]
    eq_(("org.codehaus.mojo", "simplest", "jar", "1.0"),
        resolved.dependencies.values()[0].versioned)
    eq_(initialdepcount, len(reso))

def test_version_override():
    reso = createreso('test/goodpoms/multiversion')
    resolved = reso[('org.codehaus.mojo', 'useruser', 'jar', '1.0')]

    eq_([("org.codehaus.mojo", "simplest1user", "jar", "1.0"),
        ("org.codehaus.mojo", "simplest11user", "jar", "1.0"),
        ("org.codehaus.mojo", "simplest", "jar", "1.0")],
        [dep.versioned for dep in resolved.dependencies.values()])

def test_localrepo():
    reso = maven.Resolver()
    reso.addlocalrepo('test/repo')
    reso.addpom(maven.parse('test/goodpoms/basic/simplestuser.xml'))
    reso.resolve()
    resolved = reso[('org.codehaus.mojo', 'simplestuser', 'jar', '1.0')]

    eq_(set(), resolved.missing)
    eq_([("org.codehaus.mojo", "simplest", "jar", "1.0")],
        [dep.versioned for dep in resolved.dependencies.values()])
