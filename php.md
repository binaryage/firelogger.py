---
title: FireLogger for PHP
subtitle: a sexy PHP logger console integrated into Firebug
layout: product
icon: /shared/img/firelogger4php-icon.png
repo: http://github.com/darwin/firelogger4php
support: http://github.com/darwin/firelogger4php/issues
downloadtitle: Install v0.7
download: https://addons.mozilla.org/en-US/firefox/addon/11090
downloadboxwidth: 210px
donate: https://addons.mozilla.org/en-US/firefox/addons/contribute/11090?source=addon-detail
subdownload: 
subdownloadlink:
mainshot: /shared/img/firelogger4php-mainshot.png
mainshotfull: /shared/img/firelogger4php-mainshot-full.png
overlaysx: 1120px
overlaysy: 986px
overlaycx: 25px
overlaycy: 10px
permalink: /php
---

<div class="advertisement">
    <ul class="header-menu php">
        <li><a class="menu-item-python" href="/">python</a></li>
        <li><a class="menu-item-php" href="/php">php</a></li>
    </ul>
</div>

## Features

#### You get `flog` function which is modeled after Firebug's `console.log`. Throw anything into it and it gets intelligently presented into console.

#### See [sample screenshot](/shared/img/firelogger4php-mainshot-full.png) for usage scenarios

* Doing also client-side development? Your log messages get displayed right under your fingerprints in Firebug, the way you like!
* Support for rich-text logging (logged objects are sent as JSON object, you may drill down their structure)
* Support for exceptions with stacktrace
* Support for advanced features:
  * open in Text Editor integration
  * production paths remapping
  * password protection
  * logs uncaught exceptions
  * logs errors reported by PHP
  * and more ...

### Compatibility with FireLogger extension

You know, Firebug and Firefox are moving targets. Sometimes you may get intro troubles by trying exotic combinations...

The best way is to run this on latest Firebug version with latest Firefox (this is the way I'm using it so you may get best support).

* **Version 0.7** works with:
  * alpha Firebug 1.5 + Firefox 3.5
  * Firebug 1.4.2 + Firefox 3.5
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

### Checkout also [FireLogger for Python](http://firepython.binaryage.com)

## Installation

You definitely need [Firebug 1.4 or higher][firebug]. You also have to install Firefox Addon which is called [FireLogger][firelogger].

#### Firefox Addon
Preferred way is to [install this firefox extension][firelogger] via addons.mozilla.com.

#### PHP Library

Requires PHP 5.3 or higher!

##### Download [firelogger.php here][repo]

    require 'firelogger.php';
    flog("Hello world!");

## FAQ

#### What is the difference between FireLogger and [FirePHP](http://www.firephp.org/)?
> Initially I've written [FireLogger for Python](http://firepython.binaryage.com) because I was doing some Google App Engine development. Recently I was asked to do some PHP development. I've tried FirePHP, it worked for me, but it wasn't "pixel perfect" enough to fit my personal taste :-) I'm a javascript guy quite opinionated about tools. I wanted flexible dirty logging function which is capable of eating whatever I throw into it (like firebug's `console.log`). I also prefer to have server-side logger console separated from javascript console in Firebug. I prefer reusing firebug's internal components for variables' inspection. FireLogger has the same look&feel as javascript console (you can drill down watches firebug-way, same fonts and colors, etc.). FireLogger has also some advanced features which may be handy (password protection, "open in text editor" and production paths remapping).

#### Is there something similar for Python?
> Check out [FireLogger for Python](http://firepython.binaryage.com)

#### Is there something similar for Ruby?
> Nope. I'd like to have one, but didn't find time to write server-side support. You are welcome to [hack it](http://wiki.github.com/darwin/firelogger)!

#### Clicking on source-file links in Logger panel does nothing. How can I open trace-back sources in TextMate?
> Go to Firebug Menu -> Open With Editor -> Configure editors ... like this: ![TextMate hint][textmate-hint]

#### I was unable to download/install FireLogger extension from addons.mozilla.org. Can you package latest version for me?
> Some people reported this problem too. You may [try workaround][workaround].

#### When I start Firefox and page loads I don't see any log records, what is wrong?
> This is Firefox optimization. After start Firefox brings up browser state into the point where it was when you closed it (no network activity at all). Refresh your page and you should be ok.

## History

* **v0.2** (24.08.2009)
  * [[darwin][darwin]] compatibility with FireLogger 0.7
  * [[darwin][darwin]] support for exceptions with callstack
  * [[darwin][darwin]] password protection
  * [[darwin][darwin]] checking for FireLogger extension header presence
  * [[darwin][darwin]] processing uncaught exceptions
  * [[darwin][darwin]] processing PHP errors
  * [[darwin][darwin]] reflecting private properties (requires PHP 5.3+)

* **v0.1** (17.08.2009)
  * [[darwin][darwin]] compatibility with FireLogger 0.6
  * [[darwin][darwin]] initial implementation, supports basic logging

## Links

### Sites

* **[FirePython](http://firepython.binaryage.com)** - original logging project
* **[FirePHP](http://firephp.org)** - alternative logging tool, you should check it out!

### Also thanks to

* **[Joe Hewitt, John J. Barton, Jan Odvarko and others in Firebug working group][firebug-team]** - without these guys, the web wouldn't look like today.
* **[Christoph Dorn and FirePHP contributors][firephp-authors]** - a lot of inspiration, good work mates!

[firebug]: https://addons.mozilla.org/en-US/firefox/addon/1843
[firelogger]: https://addons.mozilla.org/en-US/firefox/addon/11090
[repo]: http://github.com/darwin/firelogger4php
[workaround]: http://getsatisfaction.com/xrefresh/topics/unable_to_download_rainbow_for_firebug
[darwin]:http://github.com/darwin
[firebug-team]:http://getfirebug.com/workingGroup
[firephp-authors]:http://www.christophdorn.com/
[textmate-hint]:http://cloud.github.com/downloads/darwin/firepython/TextMateWithFirePython.png
