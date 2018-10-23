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
    global settings, insert_original, max_results, scopes, minimal_len, forbidden_prefixes
    # load all settings, for mor info look at the comments of 'DictionaryAutoComplete.sublime-settings'
    settings = sublime.load_settings('DictionaryAutoComplete.sublime-settings')
    insert_original = settings.get('insert original', False)
    max_results = int(settings.get('maximum results', 1000))
    scopes = settings.get('maximum results', ["comment", "string.quoted", "text"])
    minimal_len = max(1,settings.get('minimal length',1)) # never fire on zero length
    forbidden_prefixes = settings.get('forbidden prefixes',[])

class DictionaryAutoComplete(sublime_plugin.EventListener):
    request_load = True
    last_language = ""
    word_dict_list = {}

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
            try:
                if ST3:
                    words = sublime.load_binary_resource(dictionary).decode(encoding).splitlines()
                else: #ST2
                    dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                    words = open(dict_path, encoding=encoding, mode='r').read().splitlines()
                words = [word.split('/')[0].split('\t')[0] for word in words]
            except Exception as e:
                print('[DictionaryAutoComplete] Error reding from dictionary : ' + e)

            # optimise the list
            del words[0:1]
            words = [word for word in words if len(word) >= minimal_len]
            # create dictionary of prefix -> list of words
            self.word_dict_list = {}
            for word in words:
                pref = word[:minimal_len].lower()
                if not pref in self.word_dict_list:
                    self.word_dict_list[pref] = []
                self.word_dict_list[pref].append(word)
            print("[DictionaryAutoComplete] Number of words: ", len(words))
            print("[DictionaryAutoComplete] First ones: ", words[:10])
            print("[DictionaryAutoComplete] Nomber of prefixes of length ",minimal_len," : ", len(self.word_dict_list))


    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        # prepare the prefix to search for
        if prefix.istitle():
            def correctCase(x): return x[:1].upper()+x[1:] if x.islower() else x
        elif prefix.isupper():
            def correctCase(x): return x.upper() if x.islower() else x
        else:
            def correctCase(x): return x
        prefix = prefix.lower()

        # filter relevant items:
        index = 0
        autocomplete_list = []
        pref = prefix[:minimal_len] # a lower case prefix to look in the dictionary
        suff = prefix[minimal_len:] # a lower case suffixe to look in the list of words
        prefix_length = len(prefix)
        if pref in self.word_dict_list:
            for w in self.word_dict_list[pref]:
                if minimal_len == prefix_length or w[minimal_len:prefix_length].lower() == suff:
                    w = correctCase(w)
                    autocomplete_list.append((w,w))
                    index = index +1
                    if index > max_results:
                        break

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

    def is_scope_ok(self, view, point):
        # check if the cursor position is in allowed scope
        for selector in scopes:
            if view.match_selector(point, selector):
                return True
        return False

    def is_forbidden_prefix(self, view, prefix, point):
        # get the prefix character
        pos = point - len(prefix)
        ch = view.substr(sublime.Region(pos-1, pos))
        # return true if it is forbidden
        return ch in forbidden_prefixes


    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        # check the prefix length
        if len(prefix) < minimal_len:
            return None # Too short to complete
        # check if scope is allowed
        if not self.is_scope_ok(view, locations[0]):
            return None # Forbidden scope
        # check for forbidden prefixes
        if self.is_forbidden_prefix(view, prefix, locations[0]):
            return None # Forbidden prefix
        # get the auto-completion list
        return self.get_autocomplete_list(view, prefix)

# init the plug-in in ST2
if not ST3:
    plugin_loaded()
