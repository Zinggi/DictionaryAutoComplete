Dictionary Auto-Complete
========================

![Pic](https://lh3.googleusercontent.com/-x4YM7vJ1-W4/UXVsHF5l-oI/AAAAAAAAAVk/in3aQcg7jEI/s872/4.gif)

This plug-in adds auto-completion entries from the dictionary file if you are typing inside **comments, strings or in text** files.
Useful for very lazy typers like me or if you're searching for a particular word.

In a comment, string or text file, just type **Ctrl + Space** to show auto-completion.


Alternatively, you can add this entry to your **'Settings - User'** to **always show auto-completion**, regardless where you're typing:
<pre>"auto_complete_selector": "source, text"</pre>


DictionaryAutoComplete takes the suggestions from the dictionary used for spell-checking, so if you want to use another dictionary,
change <pre>"dictionary": "Packages/Language - English/en_US.dic"</pre> to your preferred dictionary.
If you do so, you might also have to change the encoding setting under 'Preferences' -> 'Package Settings' -> 'DictionaryAutoComplete' -> 'Settings User' to the encoding of your dictionary file. (try UTF-8)
<pre>{
	"encoding": "ISO-8859-1"
}</pre>


Installation
------------
**Very easy with [Package Control](http://wbond.net/sublime_packages/package_control) right inside Sublime Text 2 (Package Control needs to be installed):**

1.	Ctrl + shift + P
2.  Search for "inst", hit enter
3.  Search for "DictionaryAutoComplete", hit enter

**Manually (not recommended):**

1.  Clone or download this package
2.	Put it into your Packages directory (find using 'Preferences' -> 'Browse Packages...')


This was really easy to develop compared to [UnrealScript IDE](https://github.com/Zinggi/UnrealScriptIDE#unrealscript-ide-plug-in-for-sublime-text-2). If you still think I've earned a beer, there you go: :wink:  
[![Donate](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XT5LYESK99ESA)


* * *
License
------------
Dictionary Auto-Complete for Sublime Text 2
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