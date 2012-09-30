import collections
import os
import maven
import Queue
import re
import threading
import zipfile

packageline = re.compile("^\s*package ([\w.]+);\s*$")

pathtofull = lambda path: '.'.join(path.split('/'))

ClassLoc = collections.namedtuple("ClassLoc", ["classname", "path"])

class Lookup(object):
    def __init__(self):
        self.resolver = maven.Resolver()
        self.modlock = threading.RLock()
        self.actions = Queue.Queue()
        self.actor = threading.Thread(target=self._processactions, name="LookupActor")
        self.actor.daemon = True
        self.actor.start()

    def addroots(self, roots):
        completionevent = threading.Event()
        self.actions.put((self._addrootsaction, roots, completionevent))
        return completionevent

    def removeroots(self, roots):
        pass

    def getclassesforpath(self, path):
        with self.modlock:
            pom = self.resolver.find_pom_for_srcroot(path)
            print "Got", pom.coordinate, "for", path, "with", pom.dependencies.keys()
            return (classloc for coord in [pom.coordinate] + pom.dependencies.keys() for classloc in self.resolver[coord].srcclasses)

    def _processactions(self):
        while True:
            action, arg, oncompletion = self.actions.get()
            action(arg)
            oncompletion.set()

    def _addrootsaction(self, roots):
        print "Adding roots", [os.path.abspath(root) for root in roots]
        # TODO only count as a newpom if it's not already present
        newpoms = []
        for root in roots:
            for fn in maven.findpoms(os.path.abspath(root)):
                print "Adding pom", fn
                newpoms.append(maven.parse(fn))
        # TODO add roots to watchdog
        for newpom in newpoms:
            newpom.srcclasses = [classloc for root in newpom.srcdirs for classloc in get_classes_in_root(root)]
            newpom.testclasses = [classloc for root in newpom.testsrcdirs for classloc in get_classes_in_root(root)]
        with self.modlock:
            for newpom in newpoms:
                self.resolver.addpom(newpom.path, newpom)
            self.resolver.resolve()
            # TODO log missing from poms


def get_classes_in_root(root):
    rootlen = len(root) + 1
    for d, dns, fns in os.walk(root):
        package = pathtofull(d[rootlen:]) + "."
        for fn in (fn for fn in fns if fn.endswith('.java')):
            yield ClassLoc(package + fn.split('.')[0], os.path.join(d, fn))
        dns[:] = (d for d in dns if d != '.svn')

def get_classes(pom, test=False):
    if pom.path is not None:

        for dir in pom.srcdirs:
            for klass in get_classes_in_root(dir):
                yield klass
        if test:
            for dir in pom.testsrcdirs:
                for klass in get_classes_in_root(dir):
                    yield klass
    else:
        docjar = '%s/%s-%s-javadoc.jar' % (os.path.dirname(pom.location), pom.artifactId, pom.version)
        if os.path.exists(docjar):
            jar = zipfile.ZipFile(docjar)
            names = jar.namelist()
            jar.close()
            for name in names:
                if not name.endswith('.html') or '-' in name or name == 'index.html':
                    continue
                yield name[:-5]

def get_accessible_classes(resolver, path, contents=None):
    path = os.path.abspath(path)
    dirname, basename = os.path.split(path)
    # Find pom from location
    srcroot = dirname
    if contents:
        packagematch = packageline.search(contents)
        if packagematch:
            package = packagematch.group(1)
            srcroot = dirname[:len(package)]
    pom = resolver.find_pom_for_srcroot(srcroot)
    if pom is None:
        # If no poms, return project classes and JDK or Android
        return []
    else:
        return [klass for coord in [pom.coordinate] + pom.dependencies.keys() for klass in get_classes(resolver[coord])]
