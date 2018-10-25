# This Python file uses the following encoding: utf-8
#-----------------------------------------------------------------------------------
# Dictionary Auto-Complete
#-----------------------------------------------------------------------------------
#
# This plug-in adds auto-completion entries from the dictionary file.
# useful for very lazy typers or if you're searching for a particular word.
#
# (c) Florian Zinggeler
# (c) Kroum Tzanev
#-----------------------------------------------------------------------------------
import sublime, sublime_plugin
import os

ST3 = int(sublime.version()) >= 3000

if not ST3:
    from codecs import open

def get_setting(lang=None):
    """
    Read all the settings from previously initialized global settings.
    This function is called when the language is changed (or initialized).
    All the setting variables are global (for this module).
    """
    global dict_encoding, insert_original, max_results, allowed_scopes, minimal_len, forbidden_prefixes, local_dictionary
    print("[DictionaryAutoComplete] Get parameters for ",lang)
    # set the default values (language independent)
    dict_encoding = settings.get('encoding', 'UTF-8')
    insert_original = settings.get('insert original', False)
    max_results = int(settings.get('maximum results', 1000))
    allowed_scopes = settings.get('scopes', ["comment", "string.quoted", "text"])
    minimal_len = max(1,settings.get('minimal length',1)) # never fire on zero length
    forbidden_prefixes = settings.get('forbidden prefixes',[])
    local_dictionary = settings.get('dictionary', None)
    # set the language independent values
    if lang:
        languages = settings.get("languages",{})
        if lang in languages:
            local_settings = languages[lang]
            dict_encoding = local_settings.get('encoding', dict_encoding)
            insert_original = local_settings.get('insert original', insert_original)
            max_results = local_settings.get('maximum results', max_results)
            allowed_scopes = local_settings.get('maximum results', allowed_scopes)
            minimal_len = local_settings.get('minimal length', minimal_len)
            forbidden_prefixes = local_settings.get('forbidden prefixes', forbidden_prefixes)
            local_dictionary = local_settings.get('dictionary', local_dictionary)

def plugin_loaded():
    """
    This method is (automatically in ST3) loaded when the plug-in is ready.
    It reads the global variable `settings` from 'DictionaryAutoComplete.sublime-settings'.
    """
    global settings
    print('[DictionaryAutoComplete] plug-in is loaded.')
    # declare the settings parameters as global variables
    # load all settings, for more info look at the comments of 'DictionaryAutoComplete.sublime-settings'
    settings = sublime.load_settings('DictionaryAutoComplete.sublime-settings')
    get_setting()

class DictionaryAutoComplete(sublime_plugin.EventListener):
    request_load = True # used to avoid multiple calls of on_activated_async
    last_language = "" # used to optimize the dictionary load in load_completions
    word_dict_list = {} # the entire dictionary as {"pref" : ["prefix", "Prefab", ...], ...}

    def on_activated_async(self, view):
        """
        Called by ST on the first activation of the view.
        It calls load_completions asynchronously.
        """
        if self.request_load:
            self.request_load = False
            sublime.set_timeout(lambda: self.load_completions(view), 3)
            view.settings().add_on_change('dictionary', lambda: self.load_completions(view))

    def load_completions(self, view):
        """
        Create the word_dict_list containing all the words of the dictionary.
        The format of word_dict_list is
            {"pref" : ["prefix", "Prefab", ...], ...}
        where the length of "pref" is determined by `minimal_len` global setting variable.
        This method is called on the first activation of the view and when the dictionary (language) is changed.
        If this method is called without a language change it simply returns.
        """
        dictionary = view.settings().get('dictionary')
        if not dictionary:
            return
        language = os.path.splitext(os.path.basename(dictionary))[0]
        if self.last_language != language:
            self.last_language = language
            get_setting(language)
            if local_dictionary:
                dictionary = local_dictionary
                print("[DictionaryAutoComplete] Load dictionary from " + dictionary + " [" + dict_encoding + "]")
            else:
                print("[DictionaryAutoComplete] Load standard dictionary: " + language + " [" + dict_encoding + "]")
            try:
                if ST3:
                    words = sublime.load_binary_resource(dictionary).decode(dict_encoding).splitlines()
                else: #ST2
                    dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                    words = open(dict_path, encoding=dict_encoding, mode='r').read().splitlines()
                words = [word.split('/')[0].split('\t')[0] for word in words]
            except Exception as e:
                print('[DictionaryAutoComplete] Error reading from dictionary : ' + e)

            # optimize the list
            # the first line of .dic file is the number of words
            if not local_dictionary:
                del words[0:1]
            # keep only words longer than the minimal prefix length
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
            print("[DictionaryAutoComplete] Number of prefixes of length ",minimal_len," : ", len(self.word_dict_list))


    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        """
        Returns the auto-completion list.
        In general it is called when the prefix has the minimal length.
        And then it is called when ST consider that it is appropriate.
        In general it is not called on every key press.
        """
        autocomplete_list = [] # the list of tuples to return

        # prepare the prefix to search for
        if prefix.istitle():
            def correctCase(x): return x[:1].upper()+x[1:] if x.islower() else x
        elif prefix.isupper():
            def correctCase(x): return x.upper() if x.islower() else x
        else:
            def correctCase(x): return x
        prefix_lower = prefix.lower()
        prefix_length = len(prefix_lower)
        pref = prefix_lower[:minimal_len] # a lower case prefix to look in the dictionary
        suff = prefix_lower[minimal_len:] # a lower case suffix to look in the list of words

        # check the prefix length
        if prefix_length >= minimal_len:
            # filter relevant items
            index = 0
            if pref in self.word_dict_list:
                for w in self.word_dict_list[pref]:
                    if minimal_len == prefix_length or w[minimal_len:prefix_length].lower() == suff:
                        w = correctCase(w)
                        autocomplete_list.append((w,w))
                        index = index +1
                        if index > max_results:
                            break

        # append the original auto-complete list ?
        preventDefault = False # by default (if insert_original=='default')
        if insert_original == 'before':
            st_list = [(prefix+'\t'+w,w) for w in view.extract_completions(prefix) if w[:prefix_length].lower() == prefix_lower]
            autocomplete_list =  st_list + autocomplete_list
            preventDefault = True
        elif insert_original == 'after':
            st_list = [(prefix+'\t'+w,w) for w in view.extract_completions(prefix) if w[:prefix_length].lower() == prefix_lower]
            autocomplete_list = autocomplete_list + st_list
            preventDefault = True
        elif insert_original == 'none':
            preventDefault = True

        if preventDefault:
            return (autocomplete_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        return autocomplete_list

    def is_scope_ok(self, view, point):
        """
        Check if the cursor position is in allowed_scopes (setting).
        Called by on_query_completions to decide if it should call get_autocomplete_list.
        Return True if the scope is allowed.
        """
        for selector in allowed_scopes:
            if view.match_selector(point, selector):
                return True
        return False

    def is_forbidden_prefix(self, view, prefix, point):
        """
        Check if the character before the completion prefix is in the forbidden_prefixes (setting).
        Called by on_query_completions to decide if it should call get_autocomplete_list.
        Return True if the prefix follows forbidden character.
        """
        # get the prefix character
        pos = point - len(prefix)
        ch = view.substr(sublime.Region(pos-1, pos))
        return ch in forbidden_prefixes


    def on_query_completions(self, view, prefix, locations):
        """
        Called when ST needs an auto-completion.
        In general it is not called on every key press but only when ST needs more items for list.
        Returns the result of get_autocomplete_list if DictionaryAutoComplete is allowed in this place.
        """
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
