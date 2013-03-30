#-----------------------------------------------------------------------------------
# Dictionary Auto-Complete
#-----------------------------------------------------------------------------------
#
# This plug-in adds auto-completion entries from the dictionary file.
# useful for very lazy typers or if you're searching for a particular word.
#
# (c) Florian Zinggeler
#-----------------------------------------------------------------------------------
import sublime
import sublime_plugin
import os


class DictionaryAutoComplete(sublime_plugin.EventListener):
    settings = None
    b_first_edit = True
    b_fully_loaded = True
    word_list = []

    # on first modification in comments, get the dictionary and save it.
    def on_modified(self, view):
        if self.b_first_edit and self.b_fully_loaded:
            self.b_fully_loaded = False
            sublime.set_timeout(lambda: self.load_completions(view), 3)

    def load_completions(self, view):
        scope_name = view.scope_name(view.sel()[0].begin())       # sublime.windows()[0].active_view()
        if "comment" in scope_name or "string.quoted" in scope_name:
            if not self.settings:
                self.settings = sublime.load_settings('Preferences.sublime-settings')

                self.dict_path = os.path.join(sublime.packages_path()[:-9], self.settings.get('dictionary'))
                self.dict_path = self.dict_path.replace("/", "\\")
                print self.dict_path
                with open(self.dict_path, 'r') as dictionary:
                    words = dictionary.read().split('\n')
                    for word in words:
                        word = word.split('/')[0]
                        self.word_list.append(word)
                self.b_first_edit = False
        else:
            self.b_fully_loaded = True

    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, word):
        autocomplete_list = []

        # filter relevant items:
        for w in self.word_list:
            try:
                if word.lower() in w.lower():
                    autocomplete_list.append((w, w))
            except UnicodeDecodeError:
                continue

        return autocomplete_list

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())
        if "comment" in scope_name or "string.quoted" in scope_name:
            return (self.get_autocomplete_list(prefix), sublime.INHIBIT_EXPLICIT_COMPLETIONS)
