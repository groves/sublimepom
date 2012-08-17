import os
import re
import zipfile

packageline = re.compile("^\s*package ([\w.]+);\s*$")

pathtofull = lambda path: '.'.join(path.split('/'))

def get_classes_in_root(root):
    rootlen = len(root) + 1
    for d, dns, fns in os.walk(root):
        package = pathtofull(d[rootlen:]) + "."
        for fn in fns:
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


def get_accessible_classes(repo, path, contents):
    path = os.path.abspath(path)
    dirname, basename = os.path.split(path)
    # Find pom from location
    packagematch = packageline.search(contents)
    if packagematch:
        package = packagematch.group(1)
        srcroot = dirname[:len(package)]
    else:
        package = ''
        srcroot = dirname
    pom = repo.findPomBySrcRoot(srcroot)
    if pom is None:
        # If no poms, return project classes and JDK or Android
        return []
    else:
        return [klass for coord in [pom.coordinate()] + pom.dependencies.keys() for klass in get_classes(repo[coord])]
