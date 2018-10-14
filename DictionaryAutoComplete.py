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
import sublime
import sublime_plugin
import os

ST3 = int(sublime.version()) >= 3000

if not ST3:
    from codecs import open

class DictionaryAutoComplete(sublime_plugin.EventListener):
    settings = None
    request_load = True
    last_language = ""
    word_list = []
    insert_original = False
    max_results = 0

    # on first activation of the view, call load_completions asynchronously
    def on_activated_async(self, view):
        self.insert_original = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('insert original',False)
        self.max_results = int(sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('maximum results',1000))
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
            frequencies = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('frequency',{})
            frequency = frequencies.get(language,False)
            if frequency:
                dictionary = frequency
                encoding = 'UTF-8'
                print("[DictionaryAutoComplete] Load frequency dictionary: " + language)
            else:
                encodings = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('encoding',{})
                encoding = encodings.get(language,'UTF-8')
                print("[DictionaryAutoComplete] Load dictionary: " + language + " [" + encoding + "]")
            if ST3:
                self.word_list = sublime.load_binary_resource(dictionary).decode(encoding).splitlines()
            else: #ST2
                dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                self.word_list = open(dict_path, encoding=encoding, mode='r').read().splitlines()
            if not frequency:
                self.word_list = [word.split('/')[0].split('\t')[0] for word in self.word_list]
            print("[DictionaryAutoComplete] Number of words: ",len(self.word_list))
            print("[DictionaryAutoComplete] First ones: ",self.word_list[:10])

    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        # prepare the prefix to search for
        if not len(prefix):
            return None
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
                    if index > self.max_results:
                        break
            except UnicodeDecodeError:
                print('Unicode error in ' + w)
                continue

        # append the original auto-complete list ?
        if self.insert_original == 'before':
            autocomplete_list = view.extract_completions(prefix) + autocomplete_list
        elif self.insert_original == 'after':
            autocomplete_list = autocomplete_list + view.extract_completions(prefix)

        return (autocomplete_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def should_trigger(self, scope):
        if 'comment' in scope or 'string.quoted' in scope or 'text' == scope[:4]:
            return True
        return False

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = view.scope_name(view.sel()[0].begin())
        if self.should_trigger(scope_name):
            return self.get_autocomplete_list(view, prefix)
