# FirePython

FirePython is a sexy Python logger console integrated into [Firebug][firebug]. 

Originally, I have created it to light up my lonely nights I was spending with [Google App Engine][appengine].

![screenshot][screenshot]

## Prerequisites

You definitely need [Firebug 1.2 or higher][firebug].

## Installation

### Firefox Addon
Preferred way is to install this firefox extension via addons.mozilla.com.
The latest version is [available here][firepython].

Warning: some people have reported they are unable to download and install extension from addons.mozilla.com. 
In this case you may [try workaround][workaround].

Here is [source repository for firefox addon][addon-homepage] with instructions how to install bleeding edge version.

### Python Library

#### The easy way

``sudo easy_install firepython``

#### The manual way

Just note, that it depends on simplejson.

Clone [project from github][homepage] in your project directory.

Or if your web project uses git for versioning, you may want to be cool and use firepython as a submodule of your git repository.
  
``git submodule add git://github.com/darwin/firepython.git firepython``

(you may want to replace last parameter with real path in your repo)

If firepython directory is not on your import paths, you need to add ``firepython`` folder into your ``sys.path``.

## Usage

### Django

After installation, enable middleware by adding its path in ``MIDDLEWARE_CLASSES``: ``firepython.middleware.FirePythonDjango``. 

### WSGI compatible

After installation, enable middleware ``firepython.middleware.FirePythonWSGI``.

### Custom usage

Look for inspiration in [middleware.py][middleware-source]

## Real world examples

  * [FirePython added to Bloog][bloog-example] (blog engine for GAE)
  * [FirePython added to DryDrop][drydrop-example] (GAE hosting engine for GitHubbers && !Pythonists)

# Current State

Version 0.2 is tested to work with alpha Firebug 1.3 and Firefox 3.1.

Version 0.3 will also work with final Firebug 1.3 + Firefox 3.1 and Firebug 1.2.1 + Firefox 3.0.4.

# Contributors

* **[Alexander Solovyov][alexander]** - python server-side library, Django and WSGI middlewares.
* **[Ivan Fedorov][ivan]** - helping out with threading issues.

### Also thanks to

* **[Joe Hewitt, John J. Barton, Jan Odvarko and others in Firebug working group][firebug-team]** - without these guys, the web wouldn't look like today.
* **[Christoph Dorn and FirePHP contributors][firephp-authors]** - a lot of inspiration, good work mates!
* **[John Paulett for jsonpickle library][jsonpickle]** - I was naively developing poor man's solution for inspecting objects in Python, but hopefully googled this gem early

# Support

### Bugs / Feature requests
[The support forum is here][support].

### IRC
IRC channel [#firepython][irc] at freenode

# Articles

* [FirePython — no prints?][firepython-no-prints] (by Alexander Solovyov)

# History

* v0.3 (to be released)
  * compatibility with Firebug 1.2
  * password protection for production site
  * path rewrite functionality
  * console supports rich formatting of python log messages
  * thread-safety
  * improved API

* v0.2 (24.11.2008)
  * Django and WSGI middlewares by Alexander Solovyov
  * added as firepython package to PyPI index
  * fixed FirePython panel styles when Firebug window was detached from main window

* v0.1 (15.11.2008) 
  * public alpha release
  * initial server-side support for Python and Google App Engine
  * communication via response headers
  * logging module functionality (debug, info, warning, error, critical)
  * log record filtering by type
  * log record searching
  * opening files in TextMate (click to timestamp field)

[screenshot]: http://github.com/darwin/firepython-addon/tree/master/support/screenshot.png?raw=true "FirePython in action"
[firebug]: https://addons.mozilla.org/en-US/firefox/addon/1843
[appengine]: http://code.google.com/appengine
[firepython]: https://addons.mozilla.org/en-US/firefox/addon/9602
[homepage]: http://github.com/darwin/firepython
[contact]: mailto:antonin@hildebrand.cz
[workaround]: http://getsatisfaction.com/xrefresh/topics/unable_to_download_rainbow_for_firebug
[support]: http://firepython.uservoice.com/
[firepython-no-prints]:http://blogg.ingspree.net/blog/2008/11/24/firepython-no-prints/
[alexander]:http://github.com/piranha
[ivan]:http://github.com/oxyum
[firebug-team]:http://getfirebug.com/workingGroup
[firephp-authors]:http://www.christophdorn.com/
[irc]:irc://irc.freenode.net/#firepython
[addon-homepage]: http://github.com/darwin/firepython-addon
[middleware-source]:http://github.com/darwin/firepython/tree/master/middleware.py
[jsonpickle]:http://code.google.com/p/jsonpickle/
[bloog-example]:http://github.com/DocSavage/bloog/commit/346e5fb7c1fd87259dc79f2c4ae852badb6f2b79
[drydrop-example]:http://github.com/darwin/drydrop/tree/22aadc0a463ae76e10aaefdf7aee002c7e605793/dryapp/drydrop_handler.py#L326