Dictionary Auto-Complete
========================

![Pic](https://lh3.googleusercontent.com/7ka0khetxaP2EebgUvXE7SAIOAuRAA0rN5TMMCWq51iZlQ9KmBI2XaXnQPXI5mp6LavmXosuZhNW_FV7BG16OHeGo_WZLiXYgUt8NUz719VzZUkB0Dge_jrKtNK49Hkl8L7lb14eFzad-Hf7exqrdDmznk4YivkRNbwzbCp64sWsIYHFklTMBBS2vVGv7suNwXUGPNVm1zi0V7VoPCgsQL0TrlJDYEWV5MTG_OCn3Em6Sn4zIkS5hF-AMaweD0UyTAHQfh8_r4C1Q4q6JMwD9K5sjlhFJuOI1wsc_d8u-fuyAGo3z_9vZGwcXJBxGAMqEyYWI9b7EBu9Cq5YmxHx2FdI73IyjA47oZoxRnPD1xXdoMaxLrXoKJe3UQcbmTDzHdzukfETDPbEZ4khuGP9nUPOvShfUF9YAjeT0NtAmTJdvtEIP6e-dnzIX7r6LWNPLy4-j36DIyvtdWIRfgaSQ6V5qmYicclbAHVOyShlQDsjk947HqkVVvQYAyajLTIVNi79jkeh2IimMA52YOZwBLLH_fd3HcYNti3pPQDa7RfKsh-tP27lMA5AiCvjthClnRLdxA-gqCqUPmpveKYw24NsGyRt5Pu2DgXttqueJABkI0L6xyIS-UBDLjYgqA2Gvd8X0b4_lBFD5LSiryr_3kpM67S3url33aIOp024-rnugwUhiRm6PsdoKA=w872-h312-no)

This plug-in adds auto-completion entries from the dictionary file if you are typing inside **comments, strings or in text** files.
Useful for very lazy typers like me or if you're searching for a particular word.

In a comment, string or text file, just type **Ctrl + Space** to show auto-completion.


Alternatively, you can add this entry to your **'Settings - User'** to **always show auto-completion**, regardless where you're typing:
<pre>"auto_complete_selector": "source, text"</pre>


DictionaryAutoComplete takes the suggestions from frequency dictionaries or the dictionary used for spell-checking, so if you want to use another dictionary, modify `DictionaryAutoComplete.sublime-settings` in the `Package Settings > DictionaryAutoComplete > Settings - User` menu.

Settings
--------

For examples of how to use the settings look at the default `DictionaryAutoComplete.sublime-settings`.

- `encoding`: set the standard dictionary encoding. It is used only if you do not set a frequency dictionnary for the corresponding language.
- `frequency`: set the frequency dictionary to be used. For more information look at the [About the frequency dictionaries](#about-the-frequency-dictionaries) section.
- `insert original`: indicate if the original auto-completion (containing the words of the current file) should be appended `before`, `after` or `none`.
- `maximum results`: indicate the maximum auto-completion suggestions to return.


Installation
------------
**Very easy with [Package Control](http://wbond.net/sublime_packages/package_control) right inside Sublime Text 2/3 (Package Control needs to be installed):**

1.	Ctrl + shift + P
2.  Search for "inst", hit enter
3.  Search for "DictionaryAutoComplete", hit enter

**Manually (not recommended):**

1.  Clone or download this package
2.	Put it into your Packages directory (find using 'Preferences' -> 'Browse Packages...')


This was really easy to develop compared to [UnrealScript IDE](https://github.com/Zinggi/UnrealScriptIDE#unrealscript-ide-plug-in-for-sublime-text-2). If you still think I've earned a beer, there you go: :wink:
[![Donate](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XT5LYESK99ESA)

About the frequency dictionaries
--------------------------------
This package comes with frequency dictionaries obtained from [LuminosoInsight/wordfreq](https://github.com/LuminosoInsight/wordfreq) project.
The corresponding dictionaries were transformed to `.txt` files with one word per line (the more frequents come first) by keeping only the words longer than 5 characters.

The transformation use [jakm/msgpack-cli](https://github.com/jakm/msgpack-cli) tool to convert the `.msgpack` files to `.json` files, and then using `sed` and `grep` they are transformed to `.txt` files with one word per line.

The `bash` script that do this is in the sub folder `freq_script`.
The resulting frequency dictionaries are in the sub folder `freq_dicts`.

* * *
License
-------
Dictionary Auto-Complete for Sublime Text 2/3
Copyright (C) 2013 Florian Zinggeler

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
