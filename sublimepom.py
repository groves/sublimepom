import sublime
import sublime_plugin
import webbrowser

import nav
import maven
reload(nav)
reload(maven)

lookup = nav.Lookup()

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
        lookup.removeroots(addedfolders - currentfolders)
        lookup.addroots(currentfolders - addedfolders)
        addedfolders = currentfolders

class OpenJavaClass(sublime_plugin.TextCommand):
    def run(self, edit):
        fn = self.view.file_name()
        if fn is None or not fn.endswith('.java'):
            return
        options = list(lookup.getclassesforpath(fn))

        def x(result):
            if result != -1:
                fn = options[result][1]
                if fn.endswith('.java'):
                    self.view.window().open_file(fn)
                else:
                    webbrowser.open_new(fn)

        self.view.window().show_quick_panel([t[0] for t in options], x)
