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

ST3 = int(sublime.version()) > 3000

class DictionaryAutoComplete(sublime_plugin.EventListener):
    settings = None
    request_load = True
    last_language = ""
    print(last_language)
    word_list = []
    insert_original = False
    max_results = 0

    # on first activation of the view, call load_completions asynchronously
    def on_activated_async(self, view):
        self.insert_original = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('insert original',False)
        self.max_results = int(sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('max num results',1000))
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
            encodings = sublime.load_settings('DictionaryAutoComplete.sublime-settings').get('encoding',{})
            encoding = encodings.get(language,'UTF-8')
            print("Load dictionary : " + language + " [" + encoding + "]")
            if ST3:
                words = sublime.load_binary_resource(dictionary).decode(encoding).splitlines()
            else: #ST2
                self.dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                words = open(self.dict_path, 'r').read().decode(encoding).splitlines()
            self.word_list = [word.split('/')[0].split('\t')[0] for word in words]

    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, word):
        # prepare the word to search for
        if not len(word):
            return None
        if word[0].isupper():
            def correctCase(x): return x.title()
        else:
            def correctCase(x): return x
        word = word.lower()

        # filter relevant items:
        index = 0
        autocomplete_list = []
        for w in self.word_list:
            try:
                if w.startswith(word):
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
            autocomplete_list = view.extract_completions(word) + autocomplete_list
        elif self.insert_original == 'after':
            autocomplete_list = autocomplete_list + view.extract_completions(word)

        return autocomplete_list

    def should_trigger(self, scope):
        if 'comment' in scope or 'string.quoted' in scope or 'text' == scope[:4]:
            return True
        return False

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())
        if self.should_trigger(scope_name):
            return self.get_autocomplete_list(view, prefix)
