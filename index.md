---
title: FireLogger
subtitle: a sexy logger console integrated into Firebug
layout: product
icon: /shared/img/firepython-icon.png
repo: http://github.com/darwin/firelogger
support: http://github.com/darwin/firelogger/issues
downloadtitle: Install v0.7
download: https://addons.mozilla.org/en-US/firefox/addon/11090
downloadboxwidth: 210px
donate: https://addons.mozilla.org/en-US/firefox/addons/contribute/11090?source=addon-detail
subdownload: 
subdownloadlink:
mainshot: /shared/img/firepython-mainshot.png
mainshotfull: /shared/img/firepython-mainshot-full.png
overlaysx: 1606px
overlaysy: 738px
overlaycx: 25px
overlaycy: 10px
---

<div class="advertisement">
    <ul class="header-menu python">
        <li><a class="menu-item-python" href="/">python</a></li>
        <li><a class="menu-item-php" href="/php">php</a></li>
    </ul>
</div>

## Features

* Your logging messages are displayed right under your fingerprints in Firebug
* Support for rich-text logging (logged objects are sent as JSON object, you may drill down their structure)
* Support for exceptions and backtrace visualization
* Support for profiling graphs
* Ready as WSGI middleware and Django middleware
* Support for advanced features:
  * open in Text Editor integration
  * production paths remapping
  * password protection
  * logging proxy support
  * and more ...

### Compatibility

* **Version 0.6** works with:
  * alpha Firebug 1.5 + Firefox 3.5
  * Firebug 1.4.2 + Firefox 3.5
* **Version 0.5** works with:
  * beta Firebug 1.4 + Firefox 3.0.x or Firefox 3.5
  * does not work with Firebug 1.3 and older!
* **Version 0.4** works with:
  * Firebug 1.3 + Firefox 3.1 
  * Firebug 1.2.1 + Firefox 3.0.4. 
  * does not work with Firebug 1.4 alpha!
* **Version 0.3** works with:
  * Firebug 1.3 + Firefox 3.1 
  * Firebug 1.2.1 + Firefox 3.0.4. 
* **Version 0.2** is tested to work with alpha Firebug 1.3 and Firefox 3.1.

## Installation

You definitely need [Firebug 1.4 or higher][firebug]. You also have to install Firefox Addon which is called [FireLogger][firelogger].

### Easy Installation

#### Firefox Addon
Preferred way is to [install this firefox extension][firelogger] via addons.mozilla.com.

#### Python Library

``sudo easy_install firepython``

### Install from sources

#### Firefox Addon

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

#### Python Library

Just note, that it depends on simplejson (or some other json parsing library needed by [jsonpickle][jsonpickle]).

Clone [project from github][homepage] in your project directory.

``git clone git://github.com/darwin/firepython.git``

Or if your web project uses git for versioning, you may want to be cool and use firepython as a submodule of your git repository.
  
``git submodule add git://github.com/darwin/firepython.git relative/path/to/firepython``

In case firepython directory is not on your import paths, you need to add ``relative/path/to`` folder into your ``sys.path``.

## Usage

#### Django

After installation, enable middleware by adding its path in ``MIDDLEWARE_CLASSES``: ``firepython.middleware.FirePythonDjango``. 

#### WSGI compatible

After installation, enable middleware ``firepython.middleware.FirePythonWSGI``.

#### Custom usage

Look for inspiration in [middleware.py][middleware-source]

### Real world examples

* [FirePython added to Bloog][bloog-example] (blog engine for GAE)
* [FirePython added to DryDrop][drydrop-example] (GAE hosting engine for GitHubbers && !Pythonists)
* [FirePython added to Pyxer](http://code.google.com/p/pyxer/wiki/FirePython) (Python web framework)

## FAQ

#### logging.debug("hello world!") outputs nothing, what is wrong?
> Default behavior of logging module is to output logs up from level INFO. Run "logging.getLogger().setLevel(logging.DEBUG)" to see all logs.

#### Is there something similar for PHP?
> Check out [FireLogger for PHP](http://firelogger4php.binaryage.com), you may also want to checkout alternative logging tool [FirePHP](http://firephp.org)

#### Is there something similar for Ruby?
> Nope. I'd like to have one, but didn't find time to write server-side support. You are welcome to [hack it](http://wiki.github.com/darwin/firelogger)!

#### How can I change the name of the default logger?
> logging.getLogger().name = "my logger"

#### How can I open preferences?
> Switch to Logger panel and look to Firebug's toolbar. There is a green bug icon. It is a menu button! <a href="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerMenuButton.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerMenuButton.png"></a><br/><a href="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerPreferences.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/FireLoggerPreferences.png"></a>

#### Clicking on source-file links in Logger panel does nothing. How can I open trace-back sources in TextMate?
> Go to Firebug Menu -> Open With Editor -> Configure editors ... like this: ![TextMate hint][textmate-hint]

#### I was unable to download/install FireLogger extension from addons.mozilla.org. Can you package latest version for me?
> Some people reported this problem too. You may [try workaround][workaround].

#### How can I see Python profiling graph?
> 1. enable this feature in FireLogger preferences
> 2. setup a editor in External Editors in Firebug called "Graphviz" (the name is important!). It should be path to executable of a viewer for .dot graphs.
> 3. reload page and you should see info log line containing profiling info, clicking on the line launches configured Graphviz viewer (a filename will be passed as the first parameter)
<a href="http://cloud.github.com/downloads/darwin/firelogger/ExternalEditorsConfiguration.png"><img src="http://cloud.github.com/downloads/darwin/firelogger/ExternalEditorsConfiguration.png"></a><br>
<a href="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphLog.png"><img src="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphLog.png"></a><br>
<a href="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphExample.png"><img src="http://cloud.github.com/downloads/darwin/firepython/FirePython-ProfilingGraphExample.png" width="600"></a>

#### When I start Firefox and page loads I don't see any log records, what is wrong?
> First page content was probably loaded from cache. Refresh your page and you should be ok.

#### My page does multiple AJAX requests to the same URL, I see logs for the first response, but not for others. Am I missing something?
> There is a bug in Firebug 1.4, it calls onResponse multiple times under some circumstances. That was very annoying, so I did a HACK and test for URL uniqueness in FireLogger. This will unfortunately filter out your multiple AJAX requests. Let's hope for fixes on Firebug side.

## History

* **v0.6** (28.06.2009)
  * [[darwin][antonin]] support for PHP (http://firelogger4php.binaryage.com)
  * [[darwin][antonin]] fixed bug when warning about disabled console and net panel was not displayed
  * [[darwin][antonin]] fixed broken "Open in external editor" functionality (FB1.5)
  * [[darwin][antonin]] compatibility with FB1.4.2
  * [[darwin][antonin]] compatibility with alpha FB1.5

* **v0.5** (28.06.2009)
  * [[darwin][antonin]] compatibility with Firebug 1.4

* **v0.4** (30.03.2009)
  * [[bslatkin][brett]] profiling graphs for Python (WSGI)
  * [[piranha][alexander]] enabled profiling support for Django
  * [[piranha][alexander]] PEP-8 code cleanup

* **v0.3** (16.03.2009)
  * [[darwin][antonin]] compatibility with Firebug 1.2
  * [[darwin][antonin]] password protection for production site
  * [[darwin][antonin]] path rewrite functionality
  * [[darwin][antonin]] console supports rich formatting of python log messages
  * [[oxyum][ivan]+[piranha][alexander]] thread-safety
  * [[darwin][antonin]] improved API
  * [[darwin][antonin]] Firefox Addon detached as a separate project FireLogger
  * [[darwin][antonin]] option for hiding internal reprs of exported objects

* **v0.2** (24.11.2008)
  * [[piranha][alexander]] Django and WSGI middlewares
  * [[piranha][alexander]] added as firepython package to PyPI index
  * [[darwin][antonin]] fixed Logger panel styles when Firebug window was detached from main window

* **v0.1** (15.11.2008) 
  * [[darwin][antonin]] public alpha release
  * [[darwin][antonin]] initial server-side support for Python and Google App Engine
  * [[darwin][antonin]] communication via response headers
  * [[darwin][antonin]] logging module functionality (debug, info, warning, error, critical)
  * [[darwin][antonin]] log record filtering by type
  * [[darwin][antonin]] log record searching
  * [[darwin][antonin]] opening files in TextMate (click to timestamp field)

## Links

### Articles

* **[Realtime logging to Firebug using FirePython](http://code.google.com/appengine/articles/firepython.html)** by Antonin Hildebrand
* **[FirePython — no prints?][firepython-no-prints]** by Alexander Solovyov
* **[Integrating FirePython with Pyxer](http://code.google.com/p/pyxer/wiki/FirePython)** by Dirk Holtwick

### Contributors

* **[Alexander Solovyov][alexander]** - python server-side library, Django and WSGI middlewares.
* **[Ivan Fedorov][ivan]** - helped out with threading issues.
* **[Brett Slatkin][brett]** - added profiling feature.

### Also thanks to

* **[Joe Hewitt, John J. Barton, Jan Odvarko and others in Firebug working group][firebug-team]** - without these guys, the web wouldn't look like today.
* **[Christoph Dorn and FirePHP contributors][firephp-authors]** - a lot of inspiration, good work mates!
* **[John Paulett for jsonpickle library][jsonpickle]** - I was naively developing poor man's solution for inspecting objects in Python, but hopefully googled this gem early
* **[Jose Fonseca for gprof2dot library][gprof2dot]** - deep Python profiling possible

[firebug]: https://addons.mozilla.org/en-US/firefox/addon/1843
[appengine]: http://code.google.com/appengine
[firelogger]: https://addons.mozilla.org/en-US/firefox/addon/11090
[homepage]: http://github.com/darwin/firepython
[contact]: mailto:antonin@hildebrand.cz
[workaround]: http://getsatisfaction.com/xrefresh/topics/unable_to_download_rainbow_for_firebug
[firepython-no-prints]:http://blogg.ingspree.net/blog/2008/11/24/firepython-no-prints/
[alexander]:http://github.com/piranha
[ivan]:http://github.com/oxyum
[brett]:http://github.com/bslatkin
[antonin]:http://github.com/darwin
[firebug-team]:http://getfirebug.com/workingGroup
[firephp-authors]:http://www.christophdorn.com/
[irc]:irc://irc.freenode.net/#binaryage
[addon-homepage]: http://github.com/darwin/firepython-addon
[middleware-source]:http://github.com/darwin/firepython/tree/master/middleware.py
[jsonpickle]:http://code.google.com/p/jsonpickle/
[bloog-example]:http://github.com/DocSavage/bloog/commit/346e5fb7c1fd87259dc79f2c4ae852badb6f2b79
[drydrop-example]:http://github.com/darwin/drydrop/tree/22aadc0a463ae76e10aaefdf7aee002c7e605793/dryapp/drydrop_handler.py#L326
[textmate-hint]:http://cloud.github.com/downloads/darwin/firepython/TextMateWithFirePython.png
[activation]:http://blog.getfirebug.com/?p=124
[gprof2dot]:http://code.google.com/p/jrfonseca/wiki/Gprof2Dot