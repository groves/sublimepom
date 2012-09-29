import os
import pom
import Queue
import re
import threading
import zipfile

packageline = re.compile("^\s*package ([\w.]+);\s*$")

pathtofull = lambda path: '.'.join(path.split('/'))


class Lookup(object):
    def __init__(self):
        self.repo = pom.Repository()
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
            return get_accessible_classes(self.repo, path)

    def _processactions(self):
        while True:
            action, arg, oncompletion = self.actions.get()
            action(arg)
            oncompletion.set()

    def _addrootsaction(self, roots):
        print "Adding roots", [os.path.abspath(root) for root in roots]
        newpoms = []
        for root in roots:
            for fn in pom.findpoms(os.path.abspath(root)):
                print "Adding pom", fn
                newpoms.append(pom.parse(fn))
        with self.modlock:
            for newpom in newpoms:
                self.repo.addpom(newpom.path, newpom)


def get_classes_in_root(root):
    rootlen = len(root) + 1
    for d, dns, fns in os.walk(root):
        package = pathtofull(d[rootlen:]) + "."
        for fn in (fn for fn in fns if fn.endswith('.java')):
            yield package + fn.split('.')[0]
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

def get_accessible_classes(repo, path, contents=None):
    path = os.path.abspath(path)
    dirname, basename = os.path.split(path)
    # Find pom from location
    srcroot = dirname
    if contents:
        packagematch = packageline.search(contents)
        if packagematch:
            package = packagematch.group(1)
            srcroot = dirname[:len(package)]
    pom = repo.find_pom_for_srcroot(srcroot)
    if pom is None:
        # If no poms, return project classes and JDK or Android
        return []
    else:
        return [klass for coord in [pom.coordinate] + pom.dependencies.keys() for klass in get_classes(repo[coord])]
