# FirePython

FirePython is a sexy Python logger console integrated into [Firebug][firebug]. 

Originally, I have created it to light up my lonely nights I was spending with [Google App Engine][appengine].

![screenshot][screenshot]

## Prerequisites

You definitely need [Firebug 1.2 or higher][firebug].

## Installation

### Version 0.2 (outdated)

Version 0.2 is quite outdated (November 2008). 
I haven't made time to do proper release of 0.3 yet. 
Are you adventurous? Skip this and check installation of latest version from sources in next section.

#### Firefox Addon
Preferred way is to [install this firefox extension][firepython] via addons.mozilla.com.

#### Python Library

``sudo easy_install firepython``

### Latest version from sources (preferred)

#### Firefox Addon

If you want to install latest addon from sources, you need to build it. 
It should be simple, but make sure you have these tools on your paths:

* git
* zip
* ruby and rake

##### Build steps:

    git clone git://github.com/darwin/firepython-addon.git
    git clone git://github.com/darwin/firepython.git
    cd firepython
    rake
  
After that your XPI should be available in ``build/firepython-X.Y.xpi``.

You should be able to install XPI file into Firefox: ``File -> Open File`` ... and browse for ``firepython-X.Y.xpi``.

Remember, that you should be also using latest FirePython library on server-side (see next section).

#### Python Library

Just note, that it depends on simplejson (or some other json parsing library needed by [jsonpickle][jsonpickle]).

Clone [project from github][homepage] in your project directory.

Or if your web project uses git for versioning, you may want to be cool and use firepython as a submodule of your git repository.
  
``git submodule add git://github.com/darwin/firepython.git relative/path/to/firepython``

Note: replace last parameter with relative path in your repo.

In case firepython directory is not on your import paths, you need to add ``relative/path/to`` folder into your ``sys.path``.

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

  * **Version 0.3** works with final Firebug 1.3 + Firefox 3.1 and Firebug 1.2.1 + Firefox 3.0.4. Btw. I'm running it with Firefox 3.2 (Nightly) + Firebug 1.4 (SVN branch)
  * **Version 0.2** is tested to work with alpha Firebug 1.3 and Firefox 3.1.

# Contributors

  * **[Alexander Solovyov][alexander]** - python server-side library, Django and WSGI middlewares.
  * **[Ivan Fedorov][ivan]** - helping out with threading issues.

### Also thanks to

  * **[Joe Hewitt, John J. Barton, Jan Odvarko and others in Firebug working group][firebug-team]** - without these guys, the web wouldn't look like today.
  * **[Christoph Dorn and FirePHP contributors][firephp-authors]** - a lot of inspiration, good work mates!
  * **[John Paulett for jsonpickle library][jsonpickle]** - I was naively developing poor man's solution for inspecting objects in Python, but hopefully googled this gem early

# Support

## FAQ

### Clicking on source-file links in FirePython panel does nothing. How can I open trace-back sources in TextMate?
> Go to Firebug Menu -> Open With Editor -> Configure editors ... like this: ![TextMate hint][textmate-hint]

### I was unable to download/install FirePython extension from addons.mozilla.org. Can you package latest version for me?
> Some people reported this problem too. You may [try workaround][workaround].


## Bugs / Feature requests
[The support forum is here][support].

## IRC
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

[screenshot]: http://cloud.github.com/downloads/darwin/firepython/FirePython-Screenshot-v0.3.png "FirePython in action"
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
[textmate-hint]:http://cloud.github.com/downloads/darwin/firepython/TextMateWithFirePython.png