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

if ST3:
    maketrans = str.maketrans
else:
    from string import maketrans
    from codecs import open

def get_setting(lang=None):
    """
    Read all the settings from previously initialized global settings.
    This function is called when the language is changed (or initialized).
    All the setting variables are global (for this module).
    """
    # the settings as global variables
    global dict_encoding, insert_original, max_results, allowed_scopes, minimal_len, forbidden_prefixes, local_dictionary, smash_characters
    # and some other global variables
    global global_settings, smash, last_language
    if not lang:
        lang = last_language
    print("[DictionaryAutoComplete] Get parameters for", lang)
    local_settings = None
    if lang:
        languages = global_settings.get("languages", {})
        if lang in languages:
            local_settings = languages[lang]
    if local_settings:
        get_setting = lambda f,d: local_settings.get(f,global_settings.get(f, d))
    else:
        get_setting = lambda f,d: global_settings.get(f, d)

    # get the settings
    dict_encoding = get_setting('encoding', 'UTF-8')
    insert_original = get_setting('insert original', False)
    max_results = int(get_setting('maximum results', 1000))
    allowed_scopes = get_setting('scopes', ["comment", "string.quoted", "text"])
    minimal_len = max(1, get_setting('minimal length', 1)) # never fire on zero length
    forbidden_prefixes = get_setting('forbidden prefixes', [])
    local_dictionary = get_setting('dictionary', None)
    smash_characters = get_setting('smash characters', None)

    # set the smash function
    if smash_characters:
        smash_from = ''.join(smash_characters)
        smash_to = ''.join([w[:1]*len(w) for w in smash_characters])
        smash_dic = maketrans(smash_from, smash_to)
        smash = lambda prefix: prefix.lower().translate(smash_dic)
    else:
        smash = lambda prefix: prefix.lower()

def plugin_loaded():
    """
    This method is (automatically in ST3) loaded when the plug-in is ready.
    It reads the global variable `settings` from 'DictionaryAutoComplete.sublime-settings'.
    """
    global global_settings, request_load, last_language, word_dict_list

    print('[DictionaryAutoComplete] plug-in is loaded.')

    # Some global variables
    request_load = True # used to avoid multiple calls of on_activated_async
    last_language = "" # used to optimize the dictionary load in load_completions
    word_dict_list = {} # the entire dictionary as {"pref" : ["prefix", "Prefab", ...], ...}
    # load all settings from 'DictionaryAutoComplete.sublime-settings'
    global_settings = sublime.load_settings('DictionaryAutoComplete.sublime-settings')
    global_settings.add_on_change("languages",get_setting)

class DictionaryAutoComplete(sublime_plugin.EventListener):

    def on_activated_async(self, view):
        global request_load
        """
        Called by ST on the first activation of the view.
        It calls load_completions asynchronously.
        """
        if request_load:
            request_load = False
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
        global last_language, word_dict_list

        dictionary = view.settings().get('dictionary')
        if not dictionary:
            return
        language = os.path.splitext(os.path.basename(dictionary))[0]
        if last_language != language:
            last_language = language
            get_setting(language)
            if local_dictionary:
                dictionary = local_dictionary
                print("[DictionaryAutoComplete] Load dictionary from ", dictionary, "[", dict_encoding, "]")
            else:
                print("[DictionaryAutoComplete] Load standard dictionary: ", language, "[", dict_encoding, "]")
            try:
                if ST3:
                    words = sublime.load_binary_resource(dictionary).decode(dict_encoding).splitlines()
                else: #ST2
                    dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                    words = open(dict_path, encoding=dict_encoding, mode='r').read().splitlines()
                words = [word.split('/')[0].split('\t')[0] for word in words]
            except Exception as e:
                print('[DictionaryAutoComplete] Error reading from dictionary:', e)

            # optimize the list
            # the first line of .dic file is the number of words
            if not local_dictionary:
                del words[0:1]
            # keep only words longer than the minimal prefix length
            words = [word for word in words if len(word) >= minimal_len]

            # create dictionary of prefix -> list of words
            word_dict_list = {}
            for word in words:
                pref = smash(word[:minimal_len])
                if not pref in word_dict_list:
                    word_dict_list[pref] = []
                word_dict_list[pref].append(word)
            print("[DictionaryAutoComplete] Number of words: ", len(words))
            print("[DictionaryAutoComplete] First ones: ", words[:10])
            print("[DictionaryAutoComplete] Number of prefixes of length ", minimal_len, " : ", len(word_dict_list))


    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        """
        Returns the auto-completion list.
        In general it is called when the prefix has the minimal length.
        And then it is called when ST consider that it is appropriate.
        In general it is not called on every key press.
        """
        global word_dict_list
        autocomplete_list = [] # the list of tuples to return

        # prepare the prefix to search for
        if prefix.istitle():
            def correctCase(x): return x[:1].upper()+x[1:] if x.islower() else x
        elif prefix.isupper():
            def correctCase(x): return x.upper() if x.islower() else x
        else:
            def correctCase(x): return x
        prefix_smashed = smash(prefix)
        prefix_length = len(prefix_smashed)
        pref = prefix_smashed[:minimal_len] # a lower case prefix to look in the dictionary
        suff = prefix_smashed[minimal_len:] # a lower case suffix to look in the list of words

        # check the prefix length
        if prefix_length >= minimal_len:
            # filter relevant items
            index = 0
            if pref in word_dict_list:
                for w in word_dict_list[pref]:
                    if minimal_len == prefix_length or smash(w[minimal_len:prefix_length]) == suff:
                        w = correctCase(w)
                        if prefix == w[:prefix_length]:
                            autocomplete_list.append((w, w))
                        else:
                            autocomplete_list.append((prefix+'\t'+w, w))
                        index = index +1
                        if index > max_results:
                            break

        # append the original auto-complete list ?
        preventDefault = False # by default (if insert_original=='default')
        if insert_original == 'before':
            st_list = [(prefix+'\t'+w, w) for w in view.extract_completions(prefix) if smash(w[:prefix_length]) == prefix_smashed]
            autocomplete_list =  st_list + autocomplete_list
            preventDefault = True
        elif insert_original == 'after':
            st_list = [(prefix+'\t'+w, w) for w in view.extract_completions(prefix) if smash(w[:prefix_length]) == prefix_smashed]
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
