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

debug = lambda *args : None

# numbers to display if `numeric shortcuts`
CIRCLE_NUMBER = "⓿❶❷❸❹❺❻❼❽❾❿"

# format the first element in an auto-complete tuple
# in case of numeric shortcuts or to avoid '...' inserted by ST
# Note:
#   - '\u00a0' is the unicode character 'NO-BREAK SPACE'
#   - '\u202f' is the unicode character 'NARROW NO-BREAK SPACE'
#   - '\u2009' is the unicode character 'THIN SPACE'
def to_display(word, prefix=None, n=None):
    if prefix:
        if numeric_shorcuts and n <= 9:
            return prefix + str(n) + '\t\u202f\u00a0' + word + '\u00a0' + CIRCLE_NUMBER[n] + '\u202f'
        else:
            return prefix + word[n:] + '\t\u202f\u00a0' + word + '\u00a0' + dictionary_symbol
    else:
        return word + '\t' + dictionary_symbol
def get_setting(lang=None):
    """
    Read all the settings from previously initialized global settings.
    This function is called when the language is changed (or initialized).
    All the setting variables are global (for this module).
    """
    # the settings as global variables
    global dict_encoding, insert_original, max_results, allowed_scopes, minimal_len, forbidden_prefixes, local_dictionary, smash_characters, print_debug, reset_on_every_key, numeric_shorcuts, dictionary_symbol
    # and some other global variables
    global global_settings, smash, last_language, debug

    if not lang:
        lang = last_language

    # try first to read the settings for the current language
    # if there are no such settings it read the default ones
    local_settings = None
    if lang:
        languages = global_settings.get("languages", {})
        if lang in languages:
            local_settings = languages[lang]
    if local_settings:
        get_parameter = lambda f, d: local_settings.get(f,global_settings.get(f, d))
    else:
        get_parameter = lambda f, d: global_settings.get(f, d)

    # get the settings
    dict_encoding = get_parameter('encoding', 'UTF-8')
    insert_original = get_parameter('insert original', 'default')
    max_results = int(get_parameter('maximum results', 1000))
    allowed_scopes = get_parameter('scopes', ["comment", "string.quoted", "text"])
    minimal_len = max(1, get_parameter('minimal length', 1)) # never fire on zero length
    forbidden_prefixes = get_parameter('forbidden prefixes', [])
    local_dictionary = get_parameter('dictionary', None)
    smash_characters = get_parameter('smash characters', None)
    print_debug = get_parameter('debug', "status")
    reset_on_every_key = get_parameter('reset on every key', False)
    numeric_shorcuts = get_parameter('numeric shortcuts', False)
    dictionary_symbol = get_parameter('dictionary symbol', '🕮')

    # set the smash function
    if smash_characters:
        smash_from = ''.join(smash_characters)
        smash_to = ''.join([w[:1]*len(w) for w in smash_characters])
        smash_dic = maketrans(smash_from, smash_to)
        smash = lambda prefix: prefix.lower().translate(smash_dic)
    else:
        smash = lambda prefix: prefix.lower()
    # in case of numeric shorcuts limit the number of results and is only for dictionary entries
    if numeric_shorcuts:
        max_results = min(max_results, 10)
        insert_original = "none"
    if "print" in print_debug:
        debug = lambda *args: print('[DictionaryAutoComplete]', *args)
    debug("Get parameters for", lang)

def plugin_loaded():
    """
    This method is (automatically in ST3) loaded when the plug-in is ready.
    It reads the global variable `settings` from 'DictionaryAutoComplete.sublime-settings'.
    """
    global global_settings, first_activated, last_language, word_dict_list, force_reload

    debug("plug-in is loaded.")

    # Some global variables
    first_activated = True # used to avoid multiple calls of on_activated_async
    last_language = "" # used to optimize the dictionary load in load_completions
    word_dict_list = {} # the entire dictionary as {"pref" : ["prefix", "Prefab", ...], ...}
    # load all settings from 'DictionaryAutoComplete.sublime-settings'
    force_reload = False # set to true when the setings are changed
    global_settings = sublime.load_settings('DictionaryAutoComplete.sublime-settings')
    global_settings.add_on_change("languages", get_setting)
    get_setting()

class DictionaryAutoComplete(sublime_plugin.EventListener):

    last_location = -2 # used only if "reset on every key" is set

    def on_activated_async(self, view):
        """
        Called by ST on the first activation of the view.
        It calls `load_completions` asynchronously.
        """
        global first_activated, force_reload

        def load_on_settings_change(force=False):
            """
            This function is called when the settings are changed.
            When the languages settings are changed the reload is forced.
            """
            global force_reload, plugin_is_active

            plugin_is_active = sublime.active_window().active_view().settings().get("dictionary_auto_complete",True)

            force_reload = force
            self.load_completions()

        if first_activated:
            first_activated = False
            view.settings().add_on_change('dictionary', load_on_settings_change)
            global_settings.add_on_change("languages", lambda: load_on_settings_change(True))
        sublime.set_timeout(load_on_settings_change, 3)

    def load_completions(self):
        """
        Create the `word_dict_list` containing all the words of the dictionary.
        The format of `word_dict_list` is
            {"pref" : ["prefix", "Prefab", ...], ...}
        where the length of "pref" is determined by `minimal_len` global setting variable.
        This method is called on the first activation of the view and when the dictionary (language) is changed.
        If this method is called without a language change it simply returns.
        """
        global last_language, word_dict_list, minimal_len, force_reload, print_debug

        view = sublime.active_window().active_view()
        dictionary = view.settings().get('dictionary')
        if not dictionary:
            return
        language = os.path.splitext(os.path.basename(dictionary))[0]
        if "status" in print_debug:
            if plugin_is_active:
                view.set_status('DictionaryAutoComplete', '' + language + ' dictionary complete+' + str(minimal_len))
            else:
                view.set_status('DictionaryAutoComplete', 'dictionary complete is disabled')
        if last_language != language or force_reload:
            force_reload = False
            last_language = language
            get_setting(language)
            if local_dictionary:
                dictionary = local_dictionary
                debug("Load dictionary from ", dictionary, "[", dict_encoding, "]")
            else:
                debug("Load standard dictionary: ", language, "[", dict_encoding, "]")
            try:
                if ST3:
                    words = sublime.load_binary_resource(dictionary).decode(dict_encoding).splitlines()
                else: #ST2
                    dict_path = os.path.join(sublime.packages_path()[:-9], dictionary)
                    words = open(dict_path, encoding=dict_encoding, mode='r').read().splitlines()
                words = [word.split('/')[0].split('\t')[0] for word in words]
            except Exception as e:
                debug("Error reading from dictionary:", e)

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
            debug("Number of words: ", len(words))
            debug("First ones: ", words[:10])
            debug("Number of prefixes of length ", minimal_len, " : ", len(word_dict_list))


    # This will return all words found in the dictionary.
    def get_autocomplete_list(self, view, prefix):
        """
        Returns the auto-completion list.
        It is called by on_query_completions when the prefix has the minimal length.
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
            self.last_location = view.sel()[0].end() # used only if "reset on every key"
            index = 0
            if pref in word_dict_list:
                for w in word_dict_list[pref]:
                    if minimal_len == prefix_length or smash(w[minimal_len:prefix_length]) == suff:
                        w = correctCase(w)
                        if numeric_shorcuts:
                            autocomplete_list.append((to_display(w, prefix, index), w)) # if numeric shortuct is asked
                        elif prefix == w[:prefix_length]:
                            if len(w) == prefix_length:
                                autocomplete_list.insert(0, (to_display(w), w)) # if exact word match
                            else:
                                autocomplete_list.append((to_display(w), w)) # if exact prefix match
                        else:
                            autocomplete_list.append((to_display(w, prefix, prefix_length), w)) # if smashed prefix match only
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
        if not plugin_is_active:
            return None # if DictionaryAutoComplete is forbidden
        # check if scope is allowed
        if not self.is_scope_ok(view, locations[0]):
            return None # Forbidden scope
        # check for forbidden prefixes
        if self.is_forbidden_prefix(view, prefix, locations[0]):
            return None # Forbidden prefix
        # get the auto-completion list
        return self.get_autocomplete_list(view, prefix)

    def on_modified_async(self, view):
        """
        By default ST do not call `on_query_completions` on every key press.
        To overcome this if we set "reset on every key: true" in the settings file,
        this methods force completion list refresh by first hiding then showing the auto-complete.
        """
        if not plugin_is_active:
            return None # if DictionaryAutoComplete is forbidden
        current_location = view.sel()[0].end()
        if numeric_shorcuts:
            if view.is_auto_complete_visible() and self.is_scope_ok(view, current_location):
                try:
                    ch = ord(view.substr(sublime.Region(current_location-1, current_location))) - ord('0')
                    if ch >= 0 and ch <=9:
                        view.run_command('commit_completion')
                except:
                    pass
        elif reset_on_every_key:
            if self.is_scope_ok(view, current_location) and (view.is_auto_complete_visible() or self.last_location == current_location+1):
                view.run_command('hide_auto_complete')
                view.run_command('auto_complete', {'disable_auto_insert': True})


# init the plug-in in ST2
if not ST3:
    plugin_loaded()
