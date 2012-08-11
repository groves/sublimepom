import collections
from xml.etree import ElementTree


class MalformedPomException(Exception):
    def __init__(self, reason):
        Exception.__init__(self, reason)


def parse(file):
    tree = ElementTree.parse(file)
    return Pom(tree)

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


class Dependency(object):
    def __init__(self, root):
        self._artifactId = requiretext(root, "artifactId")
        self._groupId = requiretext(root, "groupId")
        self._version = gettext(root, "version")  # fill in from dependencyManagement if null
        self._packaging = gettext(root, "packaging", "jar")
        self._scope = gettext(root, "scope", "compile")
        self._optional = gettext(root, "optional", "false")

        # Exclusions


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
            self.parent = Parent(parentGroupId, parentArtifactId, parentVersion, parentRelativePath)
            self._version = gettext(root, "version", self.parent.version)
            self._groupId = gettext(root, "groupId", self.parent.groupId)
        else:
            self.parent = None
            self._version = requiretext(root, "version")
            self._groupId = requiretext(root, "groupId")

        self._packaging = gettext(root, "packaging", "jar")

        self._dependencies = [Dependency(dep) for dep in root.findall("%s/%s" % (q("dependencies"), q("dependency")))]

        # To parse:

        # dependencyManagement
        # properties
        # classifier?

        # Interpolation! Get builtin properties in addition to inherited ones

        # settings.xml?
