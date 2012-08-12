import collections
import ordereddict
import os
from xml.etree import ElementTree


class MalformedPomException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        if hasattr(self, 'fn'):
            return "MalformedPomException: %s at %s" % (self.reason, self.fn)
        else:
            return "MalformedPomException: %s" % self.reason


def parse(file):
    tree = ElementTree.parse(file)
    try:
        return Pom(tree)
    except MalformedPomException as mpe:
        mpe.fn = file
        raise

pom_ns = "{http://maven.apache.org/POM/4.0.0}"
q = lambda name: pom_ns + name


def find(el, name):
    return el.find(q(name))


def gettext(el, childname, default=None):
    child = find(el, childname)
    if child is not None:
        text = child.text.strip()
        if text:
            return text
        raise MalformedPomException("%s.%s must contain text" % (el.tag, childname))
    return default


def requirechild(parent, childname):
    child = find(parent, childname)
    if child is not None:
        return child
    raise MalformedPomException("%s must contain a %s element" % (parent.tag.replace(pom_ns, ""), childname))


def requiretext(parent, childname):
    child = requirechild(parent, childname)
    text = child.text.strip()
    if text:
        return text
    raise MalformedPomException("%s.%s must contain text" % (parent.tag, childname))

Parent = collections.namedtuple("Parent", ["groupId", "artifactId", "version", "relativePath"])

Parent.tocoord = lambda x: Coordinate(x.groupId, x.artifactId, x.version, "pom")

Coordinate = collections.namedtuple("Coordinate", ["groupId", "artifactId", "version", "packaging"])


class Dependency(object):
    def __init__(self, root):
        self._artifactId = requiretext(root, "artifactId")
        self._groupId = requiretext(root, "groupId")
        self._version = gettext(root, "version")  # fill in from dependencyManagement if null
        self._packaging = gettext(root, "type", "jar")
        self._scope = gettext(root, "scope", "compile")
        self._optional = gettext(root, "optional", "false")

        # TODO wait for interpolation
        self.coordinate = Coordinate(self._groupId, self._artifactId, self._version, self._packaging)

        # Exclusions

    def __repr__(self):
        return "Dependency%s" % (self.coordinate,)


class Pom(object):
    def __init__(self, tree):
        root = tree.getroot()

        self._artifactId = requiretext(root, "artifactId")

        parent = find(root, "parent")
        if parent is not None:
            parentGroupId = requiretext(parent, "groupId")
            parentArtifactId = requiretext(parent, "artifactId")
            parentVersion = requiretext(parent, "version")
            parentRelativePath = gettext(parent, "relativePath", "../pom.xml")
            self._parent = Parent(parentGroupId, parentArtifactId, parentVersion, parentRelativePath)
            self._version = gettext(root, "version", self._parent.version)
            self._groupId = gettext(root, "groupId", self._parent.groupId)
        else:
            self._parent = None
            self._version = requiretext(root, "version")
            self._groupId = requiretext(root, "groupId")

        self._packaging = gettext(root, "packaging", "jar")

        self._dependencies = [Dependency(dep) for dep in root.findall("%s/%s" % (q("dependencies"), q("dependency")))]

        # Maven supports expressions in groupId, artifactId, version, and packaging but warns against it.
        # We're just not going to support it until we find a reasonable use case for that.
        # TODO - add an error if any of these contain expressions
        self.coordinate = Coordinate(self._groupId, self._artifactId, self._version, self._packaging)

        # To parse:

        # dependencyManagement
        # properties
        # classifier?

        # Interpolation! Get builtin properties in addition to inherited ones

        # settings.xml?

    def resolve(self, repo):
        # TODO interpolation!
        #for dep in self._dependencies:
        #    dep.interpolate(self)

        # Add dependencies breadth-first to respect the closest-to-root version setting rule
        totraverse = [self]
        if self._parent:
            # TODO Use relativePath here?
            totraverse.append(repo[self._parent.tocoord()])

        self.dependencies = ordereddict.OrderedDict()
        while totraverse:
            print "Traversing", totraverse[0].coordinate, totraverse[0]._dependencies
            self._resolve(totraverse.pop(0), repo, self.dependencies, totraverse)

    def _resolve(self, pom, repo, dependencies, totraverse):
        for dep in pom._dependencies:
            print "Looking at", dep
            if not dep.coordinate in dependencies:
                print "Adding", dep
                dependencies[dep.coordinate] = dep
                totraverse.append(repo[dep.coordinate])
                # TODO - exclusions, optional
                # TODO - track scope, allowing overrides for less-restrictive scopes


def smellslikepom(fn):
    f = open(fn)
    read = f.read(512)
    f.close()
    return '<project' in read

DEFAULT_DIR_IGNORES = set(["target", ".git", ".svn"])


def findpoms(path, followlinks=True, ignoreddirs=DEFAULT_DIR_IGNORES):
        for d, dns, fns in os.walk(path, followlinks=followlinks):
            for fn in (fn for fn in fns if fn.endswith('.xml') and smellslikepom(d + "/" + fn)):
                yield d + "/" + fn
            dns[:] = (d for d in dns if d not in ignoreddirs)


class Repository(object):
    def __init__(self):
        self.poms_by_coordinate = {}
        self.poms_by_location = {}
        self.resolved = set()

    def adddir(self, path, followlinks=True, ignoreddirs=DEFAULT_DIR_IGNORES):
        for fn in findpoms(path, followlinks, ignoreddirs):
            self.addfile(fn)

    def removedir(self, path):
        path = os.path.abspath(path)
        for pompath, pom in self.poms_by_location.items():
            if pompath.startswith(path):
                del self.poms_by_location[pompath]
                del self.poms_by_coordinate[pom.coordinate]
                self.resolved.discard(pom)

    def resolve(self, pom):
        pom.resolve(self)
        self.resolved.add(pom)

    def addfile(self, path):
        path = os.path.abspath(path)
        pom = parse(path)
        self.poms_by_location[path] = pom
        self.poms_by_coordinate[pom.coordinate] = pom

    def __getitem__(self, key):
        pom = self.poms_by_coordinate.get(key)
        if not pom:
            if isinstance(key, str):
                path = os.path.abspath(key)
                pom = self.poms_by_location.get(path)
            if not pom:
                raise KeyError("No pom for %s" % (key,))
        if pom not in self.resolved:
            self.resolve(pom)
        return pom
