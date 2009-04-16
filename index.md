---
title: FirePython
layout: wikistyle
repo: http://github.com/darwin/firepython
support: http://firelogger.uservoice.com/
download: https://addons.mozilla.org/en-US/firefox/addon/11090
version: Version 0.4
---

# FirePython is a sexy Python logger console integrated into [Firebug][firebug].

Originally, I have created it to light up my lonely nights I was spending with [Google App Engine][appengine].

<a href="http://cloud.github.com/downloads/darwin/firelogger/FireLogger-Screenshot-v0.3.png"><img class="shadow" src="http://cloud.github.com/downloads/darwin/firelogger/FireLogger-Screenshot-v0.3.png" width="900"/></a>

## Prerequisites

You definitely need [Firebug 1.2 or higher][firebug]. You also have to install Firefox Addon which is called [FireLogger][firelogger].

## Easy Installation

### Firefox Addon
Preferred way is to [install this firefox extension][firelogger] via addons.mozilla.com.

### Python Library

``sudo easy_install firepython``

## Install latest version from sources (preferred)

### Firefox Addon

If you want to install latest addon from sources, you need to build it. 
It should be simple, but make sure you have these tools on your paths:

* git
* zip
* ruby and rake

Build steps:

    git clone git://github.com/darwin/firelogger.git
    cd firelogger
    rake
  
After that your XPI should be available in ``build/firelogger-X.Y.xpi``.

You should be able to install XPI file into Firefox: ``File -> Open File`` ... and browse for ``firelogger-X.Y.xpi``.

Remember, that you should be also using latest FirePython library on server-side (see next section).

### Python Library

Just note, that it depends on simplejson (or some other json parsing library needed by [jsonpickle][jsonpickle]).

Clone [project from github][homepage] in your project directory.

``git clone git://github.com/darwin/firepython.git``

Or if your web project uses git for versioning, you may want to be cool and use firepython as a submodule of your git repository.
  
``git submodule add git://github.com/darwin/firepython.git relative/path/to/firepython``

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

Unfortunately FireLogger is broken with Firebug1.4 branch. Mainly because of changes around [Simplified Activation][activation] and API changes. Expect FireLogger 0.5 to no longer work with Firebug 1.3 and lower.

  * **Version 0.4** works with:
    * Firebug 1.3 + Firefox 3.1 
    * Firebug 1.2.1 + Firefox 3.0.4. 
    * does not work with Firebug 1.4 alpha!
  * **Version 0.3** works with:
    * Firebug 1.3 + Firefox 3.1 
    * Firebug 1.2.1 + Firefox 3.0.4. 
  * **Version 0.2** is tested to work with alpha Firebug 1.3 and Firefox 3.1.

# Contributors

  * **[Alexander Solovyov][alexander]** - python server-side library, Django and WSGI middlewares.
  * **[Ivan Fedorov][ivan]** - helped out with threading issues.
  * **[Brett Slatkin][brett]** - added profiling feature.

### Also thanks to

  * **[Joe Hewitt, John J. Barton, Jan Odvarko and others in Firebug working group][firebug-team]** - without these guys, the web wouldn't look like today.
  * **[Christoph Dorn and FirePHP contributors][firephp-authors]** - a lot of inspiration, good work mates!
  * **[John Paulett for jsonpickle library][jsonpickle]** - I was naively developing poor man's solution for inspecting objects in Python, but hopefully googled this gem early
  * **[Jose Fonseca for gprof2dot library][gprof2dot]** - deep Python profiling possible

# Support

## FAQ

### How can I open preferences?
> Switch to Logger panel and look to Firebug's toolbar. There is a green bug icon. It is a menu button!

<a href="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerMenuButton.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerMenuButton.png"></a><br/>
<a href="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerPreferences.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerPreferences.png"></a>

### Clicking on source-file links in Logger panel does nothing. How can I open trace-back sources in TextMate?
> Go to Firebug Menu -> Open With Editor -> Configure editors ... like this: ![TextMate hint][textmate-hint]

### I was unable to download/install FireLogger extension from addons.mozilla.org. Can you package latest version for me?
> Some people reported this problem too. You may [try workaround][workaround].

### How can I see Python profiling graph?

> 1. enable this feature in FireLogger preferences
> 2. setup a editor in External Editors in Firebug called "Graphviz" (the name is important!). It should be path to executable of a viewer for .dot graphs.
> 3. reload page and you should see info log line containing profiling info, clicking on the line launches configured Graphviz viewer (a filename will be passed as the first parameter)

<a href="http://cloud.github.com/downloads/darwin/firelogger/ExternalEditorsConfiguration.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/ExternalEditorsConfiguration.png"></a><br>
<a href="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphLog.png"><img src="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphLog.png"></a><br>
<a href="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphExample.png"><img src="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphExample.png" width="600"></a>

## Bugs / Feature requests
[The support forum is here][support].

## IRC
IRC channel [#firelogger][irc] at freenode

# Articles

* [FirePython — no prints?][firepython-no-prints] (by Alexander Solovyov)

# History

* v0.4 (30.03.2009)
  * [[bslatkin][brett]] profiling graphs for Python (WSGI)
  * [[piranha][alexander]] enabled profiling support for Django
  * [[piranha][alexander]] PEP-8 code cleanup

* v0.3 (16.03.2009)
  * [[darwin][antonin]] compatibility with Firebug 1.2
  * [[darwin][antonin]] password protection for production site
  * [[darwin][antonin]] path rewrite functionality
  * [[darwin][antonin]] console supports rich formatting of python log messages
  * [[oxyum][ivan]+[piranha][alexander]] thread-safety
  * [[darwin][antonin]] improved API
  * [[darwin][antonin]] Firefox Addon detached as a separate project FireLogger
  * [[darwin][antonin]] option for hiding internal reprs of exported objects

* v0.2 (24.11.2008)
  * [[piranha][alexander]] Django and WSGI middlewares
  * [[piranha][alexander]] added as firepython package to PyPI index
  * [[darwin][antonin]] fixed Logger panel styles when Firebug window was detached from main window

* v0.1 (15.11.2008) 
  * [[darwin][antonin]] public alpha release
  * [[darwin][antonin]] initial server-side support for Python and Google App Engine
  * [[darwin][antonin]] communication via response headers
  * [[darwin][antonin]] logging module functionality (debug, info, warning, error, critical)
  * [[darwin][antonin]] log record filtering by type
  * [[darwin][antonin]] log record searching
  * [[darwin][antonin]] opening files in TextMate (click to timestamp field)

[firebug]: https://addons.mozilla.org/en-US/firefox/addon/1843
[appengine]: http://code.google.com/appengine
[firelogger]: https://addons.mozilla.org/en-US/firefox/addon/11090
[homepage]: http://github.com/darwin/firepython
[contact]: mailto:antonin@hildebrand.cz
[workaround]: http://getsatisfaction.com/xrefresh/topics/unable_to_download_rainbow_for_firebug
[support]: http://firelogger.uservoice.com/
[firepython-no-prints]:http://blogg.ingspree.net/blog/2008/11/24/firepython-no-prints/
[alexander]:http://github.com/piranha
[ivan]:http://github.com/oxyum
[brett]:http://github.com/bslatkin
[antonin]:http://github.com/darwin
[firebug-team]:http://getfirebug.com/workingGroup
[firephp-authors]:http://www.christophdorn.com/
[irc]:irc://irc.freenode.net/#firelogger
[addon-homepage]: http://github.com/darwin/firepython-addon
[middleware-source]:http://github.com/darwin/firepython/tree/master/middleware.py
[jsonpickle]:http://code.google.com/p/jsonpickle/
[bloog-example]:http://github.com/DocSavage/bloog/commit/346e5fb7c1fd87259dc79f2c4ae852badb6f2b79
[drydrop-example]:http://github.com/darwin/drydrop/tree/22aadc0a463ae76e10aaefdf7aee002c7e605793/dryapp/drydrop_handler.py#L326
[textmate-hint]:http://cloud.github.com/downloads/darwin/firepython/TextMateWithFirePython.png
[activation]:http://blog.getfirebug.com/?p=124
[gprof2dot]:http://code.google.com/p/jrfonseca/wiki/Gprof2Dot