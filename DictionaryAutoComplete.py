# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# Dictionary Auto-Complete
#-----------------------------------------------------------------------------------
#
# This plug-in adds auto-completion entries from the dictionary file.
# useful for very lazy typers or if you're searching for a particular word.
#
# (c) Florian Zinggeler
#-----------------------------------------------------------------------------------
import sublime, sublime_plugin
import os

ST3 = int(sublime.version()) >= 3000

if not ST3:
    from codecs import open

def plugin_loaded():
    print('[DictionaryAutoComplete] plug-in is loaded.')
    # declar the settings parameters as global variables
    global settings, insert_original, max_results, scopes, minimal_len
    # load all settings, for mor info look at the comments of 'DictionaryAutoComplete.sublime-settings'
    settings = sublime.load_settings('DictionaryAutoComplete.sublime-settings')
    insert_original = settings.get('insert original', False)
    max_results = int(settings.get('maximum results', 1000))
    scopes = settings.get('maximum results', ["comment", "string.quoted", "text"])
    minimal_len = settings.get('minimal length',1)

class DictionaryAutoComplete(sublime_plugin.EventListener):
    request_load = True
    last_language = ""
    word_list = []

    # on first activation of the view, call load_completions asynchronously
    def on_activated_async(self, view):
        if self.request_load:
            self.request_load = False
            sublime.set_timeout(lambda: self.load_completions(view), 3)
            view.settings().add_on_change('dictionary', lambda: self.load_completions(view))

    # create the word_list containing all the words of the dictionary
    def load_completions(self, view):
        dictionary = view.settings().get('dictionary')
        language = os.path.splitext(os.path.basename(dictionary))[0]
        if self.last_language != language:
            self.last_language = language
            encodings = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('encoding', {})
            encoding = encodings.get(language, 'UTF-8')
            print("[DictionaryAutoComplete] Load standard dictionary: " + language + " [" + encoding + "]")
            if ST3:
                self.word_list = sublime.load_binary_resource(dictionary).decode(encoding).splitlines()
            else: #ST2
                dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                self.word_list = open(dict_path, encoding=encoding, mode='r').read().splitlines()
            self.word_list = [word.split('/')[0].split('\t')[0] for word in self.word_list]
            print("[DictionaryAutoComplete] Number of words: ", len(self.word_list))
            print("[DictionaryAutoComplete] First ones: ", self.word_list[:10])


    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        # prepare the prefix to search for
        if len(prefix) < minimal_len:
            return None # Nothing to complete
        if prefix[0].isupper():
            def correctCase(x): return x.title()
        else:
            def correctCase(x): return x
        prefix = prefix.lower()

        # filter relevant items:
        index = 0
        autocomplete_list = []
        for w in self.word_list:
            try:
                if w.startswith(prefix):
                    w = correctCase(w)
                    autocomplete_list.append((w,w))
                    index = index +1
                    if index > max_results:
                        break
            except UnicodeDecodeError:
                print('[DictionaryAutoComplete] Unicode error in ' + w)
                continue

        # append the original auto-complete list ?
        preventDefault = False # by default (or for example if insert_original=='default')
        if insert_original == 'before':
            autocomplete_list = [(w,w) for w in view.extract_completions(prefix)] + autocomplete_list
            preventDefault = True
        elif insert_original == 'after':
            autocomplete_list = autocomplete_list + [(w,w) for w in view.extract_completions(prefix)]
            preventDefault = True
        elif insert_original == 'none':
            preventDefault = True

        if preventDefault:
            return (autocomplete_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        return autocomplete_list

    def should_trigger(self, view, point):
        # check if the cursor position is in allowed scope
        for selector in scopes:
            if view.match_selector(point, selector):
                return True
        return False

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        if self.should_trigger(view, locations[0]):
            return self.get_autocomplete_list(view, prefix)

# init the plug-in in ST2
if not ST3:
    plugin_loaded()
