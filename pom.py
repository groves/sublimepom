import collections
from xml.etree import ElementTree


class MalformedPomException(Exception):
    def __init__(self, reason):
        Exception.__init__(self, reason)


def parse(file):
    tree = ElementTree.parse(file)
    return Pom(tree)

q = lambda name: "{http://maven.apache.org/POM/4.0.0}%s" % name


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
    raise MalformedPomException("%s must contain a %s element" % (parent.tag, childname))


def requiretext(parent, childname):
    child = requirechild(parent, childname)
    text = child.text.strip()
    if text:
        return text
    raise MalformedPomException("%s.%s must contain text" % (parent.tag, childname))

GAV = collections.namedtuple("GroupArtifactVersion", ["group", "artifact", "version"])


class Dependency(object):
    def __init__(self, root):
        self._artifact = requiretext(root, "artifactId")
        self._group = requiretext(root, "groupId")
        self._version = gettext(root, "version")  # fill in from dependencyManagement if null
        self._packaging = gettext(root, "packaging", "jar")
        self._scope = gettext(root, "scope", "compile")
        self._optional = gettext(root, "optional", "false")

        # Exclusions?


class Pom(object):
    def __init__(self, tree):
        root = tree.getroot()

        self._artifact = requiretext(root, "artifactId")

        parent = find(root, "parent")
        if parent is not None:
            self.parent = GAV(requiretext(parent, "groupId"), requiretext(parent, "artifactId"), requiretext(parent, "version"))
            self._version = gettext(root, "version", self.parent.version)
            self._group = gettext(root, "groupId", self.parent.group)
        else:
            self.parent = None
            self._version = requiretext(root, "version")
            self._group = requiretext(root, "groupId")

        self._packaging = gettext(root, "packaging", "jar")

        self._dependencies = [Dependency(dep) for dep in root.findall("%s/%s" % (q("dependencies"), q("dependency")))]

        # To parse:

        # dependencyManagement
        # properties
        # classifier?

        # Interpolation!

        # settings.xml?
