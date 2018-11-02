Dictionary Auto-Complete
========================

![Pic](https://lh3.googleusercontent.com/7ka0khetxaP2EebgUvXE7SAIOAuRAA0rN5TMMCWq51iZlQ9KmBI2XaXnQPXI5mp6LavmXosuZhNW_FV7BG16OHeGo_WZLiXYgUt8NUz719VzZUkB0Dge_jrKtNK49Hkl8L7lb14eFzad-Hf7exqrdDmznk4YivkRNbwzbCp64sWsIYHFklTMBBS2vVGv7suNwXUGPNVm1zi0V7VoPCgsQL0TrlJDYEWV5MTG_OCn3Em6Sn4zIkS5hF-AMaweD0UyTAHQfh8_r4C1Q4q6JMwD9K5sjlhFJuOI1wsc_d8u-fuyAGo3z_9vZGwcXJBxGAMqEyYWI9b7EBu9Cq5YmxHx2FdI73IyjA47oZoxRnPD1xXdoMaxLrXoKJe3UQcbmTDzHdzukfETDPbEZ4khuGP9nUPOvShfUF9YAjeT0NtAmTJdvtEIP6e-dnzIX7r6LWNPLy4-j36DIyvtdWIRfgaSQ6V5qmYicclbAHVOyShlQDsjk947HqkVVvQYAyajLTIVNi79jkeh2IimMA52YOZwBLLH_fd3HcYNti3pPQDa7RfKsh-tP27lMA5AiCvjthClnRLdxA-gqCqUPmpveKYw24NsGyRt5Pu2DgXttqueJABkI0L6xyIS-UBDLjYgqA2Gvd8X0b4_lBFD5LSiryr_3kpM67S3url33aIOp024-rnugwUhiRm6PsdoKA=w872-h312-no)

This plug-in adds auto-completion entries from the dictionary file.
Useful for very lazy typers like me or if you're searching for a particular word.

The default scopes where this plug-in is active are `comments`, `strings` and `text`. But you can customize them.

Just type <kbd>Ctrl + Space</kbd> to show auto-completion, or allow auto-complete to **always show suggestions** by changing your **'Settings - User'** for example like this:
```
"auto_complete_selector": "text, comment, string"
```

DictionaryAutoComplete takes the suggestions from the dictionary used for spell-checking by default.
But if you want you can set another one in the settings (for example a frequency dictionary).

Installation
------------
**Very easy with [Package Control](http://wbond.net/sublime_packages/package_control) right inside Sublime Text 2/3 (Package Control needs to be installed):**

1.	Ctrl + shift + P
2.  Search for "inst", hit enter
3.  Search for "DictionaryAutoComplete", hit enter

**Manually (not recommended):**

1.  Clone or download this package
2.	Put it into your Packages directory (find using 'Preferences' -> 'Browse Packages...')

Configuration
-------------
You can customize the following parameters in (a copy in `User` package folder of) `DictionaryAutoComplete.sublime-settings` :
- `encoding` : The dictionary encoding (like `"UTF-8"` or `"ISO-8859-1"`).
- `insert original` : If the default auto-completion list should be used or not.
- `maximum results` : The maximal number of results that this plug-in should return (for slower computer smaller number is better).
- `scopes` : Define the scopes where this plug-in is active.
- `minimal length` : The minimal length of a word to be completed (for slower computer you should play with this parameter to find what is optimal).
- `forbidden prefixes` : This allows to not auto-complete after some characters, which can be useful for compatibility with other plug-ins.
- `languages` : A language specific settings. Here you can overwrite all the previous settings for a particular language. Here is also the place to set an alternative dictionary if you want.
- `dictionary` : A path to alternative dictionary to use in place of the default dictionary used for spell-checking. This allows you for example to use a [frequency dictionary](https://github.com/kpym/FrequencyDictionaries/tree/master/freq_dicts_clean) that will show in first place the most used words.
- `smash characters`: Allows you to identify characters with accents in some languages. For example for French you can set
  ```
  "smash characters": ["eéèêë", "aàâä", "cç", "iîï", "oôö", "uùûü", "yÿ"]
  ```
  and then when you type "lecon" it will suggest you "leçon".
- `numeric shortcuts`: Change the way auto complete behaves. All the choices are numbered and pressing a number select the corresponding completion. If you use this setting you should probably set `maximum results` to less than 10.
- `dictionary symbol`: Is the symbol displayed on the right that is by default `🕮`. You can choose for example one of the Unicode book symbols: `📒`, `📓`, `📔`, `📕`, `📖`, `📗`, `📚`, `📜`, `🕮`.
- `reset on every key`: *[experimental]* By default ST do not refresh the auto-completion list on every key press.To overcome this we can force completion list refresh by first hiding then showing it. This is done when this setting is set to `true` (by default it is `false`).

Commands
--------
Two commands are added in the Command Palette (<kbd>Ctrl+Shift+P</kbd>):
- `Dictionary Auto Complete: Toggle` : Activate/deactivate this plug-in.
- `Auto Complete: Toggle` : Activate/deactivate the sublime auto-completion.

* * *
License
------------
Dictionary Auto-Complete for Sublime Text 2/3
Copyright (C) 2013 Florian Zinggeler
Copyright (C) 2018 Kroum Tzanev

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
