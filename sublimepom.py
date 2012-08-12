import sublime
import sublime_plugin

import pom
reload(pom)

repo = pom.Repository()

# I'd like to add to the repo on changes to the folders in the window, but I don't think there's an event for that
# This does it on save and tries to only do something when a folder is added or removed
addedfolders = set()
class RepoMaintainer(sublime_plugin.EventListener):
    def on_post_save(self, view):
        currentfolders = set()
        for window in sublime.windows():
            for folder in window.folders():
                currentfolders.add(folder)
        global addedfolders
        for dn in addedfolders - currentfolders:
            repo.removedir(dn)
        for dn in currentfolders - addedfolders:
            repo.adddir(dn)
        addedfolders = currentfolders
