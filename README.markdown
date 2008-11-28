# FirePython

FirePython is a sexy Python logger console integrated into [Firebug 1.3][firebug]. 

Originally, I have created it to light up my lonely nights I was spending with [Google App Engine][appengine].

![screenshot][screenshot]

## Prerequisites

You definitely need [Firebug 1.3][firebug].

## Installation

### Firefox Addon
Preferred way is to install this firefox extension via addons.mozilla.com.
The latest version is [available here][firepython].

Warning: some people have reported they are unable to download and install extension from addons.mozilla.com. 
In this case you may [try workaround][workaround].

### Python Library

#### The easy way:

``sudo easy_install firepython``

#### The manual way:

Clone [project from github][homepage] and copy folder [python/firepython][firepython-folder] in your project directory.
Or alternatively you may want to add folder [python][python-folder] into your ``sys.path``.

It depends on simplejson!

## Usage:

### Django

After installation, enable middleware by adding its path in ``MIDDLEWARE_CLASSES``: ``firepython.middleware.FirePythonDjango``. 

### WSGI compatible

After installation, enable middleware ``firepython.middleware.FirePythonWSGI``.

### Custom usage

In all places where you want to capture logging ...

<code>

    import firepython

    # somewhere at the beginning of your response, before any of your loggings take place:
    handler = firepython.FirePythonLogHandler()
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
  
    # ... your handler code here

    # right before serving your response back to client:
    logger.removeHandler(handler)
    handler.flush(response.add_header)   # this will add headers into response
</code>

# Current State

Version 0.2 is tested to work with alpha Firebug 1.3 and Firefox 3.1.

# Contributors

* **[Alexander Solovyov][alexander]** - python server-side library, Django and WSGI middlewares.
* **[Ivan Fedorov][ivan]** - helping out with threading issues.

### Also thanks to

* **[Firebug team][firebug-team]** - without these guys the web wouldn't look like today.
* **[FirePHP authors][firephp-authors]** - a lot of inspiration, good work mates!

# Support

### Bugs / Feature requests
[The support forum is here][support].

### IRC
IRC channel [#firepython][irc] at freenode

# Articles

* [FirePython — no prints?][firepython-no-prints] (by Alexander Solovyov)

# History

* 0.3 (to be released)
  * password protection for production site
  * thread-safety
  * improved API

* 0.2 (24.11.2008)
  * Django and WSGI middlewares by Alexander Solovyov
  * added as firepython package to PyPI index
  * fixed FirePython panel styles when Firebug window was detached from main window

* 0.1 (15.11.2008) 
  * public alpha release
  * initial server-side support for Python and Google App Engine
  * communication via response headers
  * logging module functionality (debug, info, warning, error, critical)
  * log record filtering by type
  * log record searching
  * opening files in TextMate (click to timestamp field)

[screenshot]: http://github.com/woid/firepython/tree/master/support/screenshot.png?raw=true "FirePython in action"
[firebug]: https://addons.mozilla.org/en-US/firefox/addon/1843
[appengine]: http://code.google.com/appengine
[firepython]: https://addons.mozilla.org/en-US/firefox/addon/9602
[homepage]: http://github.com/woid/firepython
[contact]: mailto:antonin@hildebrand.cz
[workaround]: http://getsatisfaction.com/xrefresh/topics/unable_to_download_rainbow_for_firebug
[support]: http://firepython.uservoice.com/
[firepython-no-prints]:http://blogg.ingspree.net/blog/2008/11/24/firepython-no-prints/
[python-folder]:http://github.com/woid/firepython/tree/master/python
[firepython-folder]:http://github.com/woid/firepython/tree/master/python/firepython
[alexander]:http://github.com/piranha
[ivan]:http://github.com/oxyum
[firebug-team]:http://getfirebug.com/workingGroup
[firephp-authors]:http://www.christophdorn.com/
[irc]:irc://irc.freenode.net/#firepython