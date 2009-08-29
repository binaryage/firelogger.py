# This is an importable rather than a standalone html file
# for a couple of reasons, not least of those being
# than as soon as we take the step toward using file system
# resources, it makes packaging more complex ...
# The other reasons can be summarized as "laziness".


FIRELOGGER_HREF = "https://addons.mozilla.org/en-US/firefox/addon/11090"
FIREPYTHON_BASE_HREF = "http://firepython.binaryage.com"
BODY_HEADER = """\
<div id="header">
<div class="container">
    <div class="header-left span-8">
        <a href="http://www.binaryage.com"
            title="Binary Age"><div class="header-logo"></div></a>
        <a href="http://twitter.com/binaryage"><div
            class="twitter" title="Follow us on Twitter"></div></a>
    </div>
</div>
</div>
"""
BODY = """\
<!DOCTYPE html>
<html>
  <head>
    <title>FirePython demo app</title>
    <link rel="stylesheet" href="__BASE__/shared/css/screen.css"
        type="text/css" media="screen, projection">
    <link rel="stylesheet" href="__BASE__/shared/css/print.css"
        type="text/css" media="print">
    <!--[if lt IE 8]>
    <link rel="stylesheet"
        href="__BASE__/shared/css/ie.css" type="text/css"
        media="screen, projection">
    <![endif]-->
    <link rel="stylesheet" href="__BASE__/shared/css/site.css" type="text/css">
  </head>
  <body>
    __BODY_HEADER__
    <div id='site'>
      <div class='container'>
        <div class='main-left span-12'>
        <div class="logo">
          <img src="__BASE__/shared/img/firepython-icon.png"
              width="32" height="32"/>
          <h1>FirePython</h1>
        </div>
          <h2 id='instructions-header'>welcome to the FirePython demo app!</h2>
          <p id='instructions'>
              Make sure you have
                <a href="__FIRELOGGER_HREF__">firelogger</a> installed,
              then hit <a href="/BORK?error=%(error)s">this link</a>
              or any other request containing 'error' in the
              <strong>QUERY_STRING</strong> to see some output in
              the firebug <strong>Logger</strong> panel.
          </p>
          <h2 id='environ-header'><abbr
            title='partial environ, that is'>environ:</abbr></h2>
          <pre id='environ'>%(environ)s</pre>
        </div>
      </div>
    </div>
  </body>
</html>
"""

# poor man's templating, ftw!
REPLACEMENTS = (
    ('__FIRELOGGER_HREF__', FIRELOGGER_HREF),
    ('__BODY_HEADER__', BODY_HEADER),
    ('__BASE__', FIREPYTHON_BASE_HREF),   # this one *last*
)

for old, new in REPLACEMENTS:
    BODY = BODY.replace(old, new)

del old, new

EXCLAMATIONS = (
    "'bye", "'dswounds", "'sblood", "'sdeath", "'sfoot", "'struth",
    "'zackly", "'zactly", '10-4', 'AIUI', 'Abyssinia', 'BFD',
    'Baruch HaShem', 'Bueller', 'CBF', 'Christ', 'Christ alive',
    'Christ almighty', 'Deo volente', 'F off', 'FTMFW', 'FTW', 'G2G',
    'GDGD', 'GIYF', 'GTH', 'God Almighty', 'God Save the King',
    'God Save the Queen', 'God bless you', 'God damn',
    'God in heaven', 'God willing', 'Goddy', 'Godspeed',
    'Gordon Bennett', 'HTH', 'Happy Thanksgiving', 'Hell no',
    'Hell yeah', 'Holy Mother', 'Holy Mother of God', "I don't think",
    'I never did', 'I say', 'I should coco', 'I should cocoa', "I'll be",
    "I'll drink to that", "I'll say", 'JFGI', 'JSYK', 'Janey Mack',
    'Jeebus', 'Jeezum Crow', 'Jeremiah', 'Jesum Crow', 'Jesus',
    'Jesus Christ', 'Jesus H. Christ', 'Jesus Harold Christ',
    'Judas Priest', 'LOL', 'Lord be praised', 'Lord love a duck',
    'Lord willing', 'MTFBWY', 'NVRM', 'O', 'OK', 'OKDK', 'OMGWTFBBQ',
    'P U', "Qapla'", 'ROTFLMAO', 'ReHi', 'Selah', 'Sieg Heil', 'TT4N',
    'XD', 'ZOMFG', 'ZOMG', '^H', '^W', 'a', "a'ight", "a'right", 'aah',
    'aargh', 'aarrghh', 'about face', 'about sledge', 'abracadabra',
    'abso-fucking-lutely', 'absolutely', 'achoo', 'ack', 'action',
    'adieu', 'adios', 'agreed', 'ah', 'ah-choo', 'aha', 'ahchoo', 'ahem',
    'ahh', 'ahoy', 'ahoy-hoy', 'ai', 'ai yah', 'alack', 'alakazam', 'alas',
    'alley oop', 'allrighty', 'alreet', 'alrighty', 'amen', 'amidships',
    'and the horse you rode in on', 'applesauce',
    'arf', 'argh', 'arr', 'arrah now', 'as if', 'as you like',
    'as you wish', 'astaghfirullah',
    'atchoo', 'atishoo', 'attaboy', 'attagirl', 'au revoir', 'avast',
    'aw', 'aw shucks',
    'aweel', 'aww', 'ay', 'ay, chihuahua', 'aye', 'aye man',
    'ba da bing ba da boom',
    'bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovar'
    'rhounawnskawntoohoohoordenenthurnuk', 'baccare', 'bad luck',
    'bada bing', 'bada bing bada boom', 'bada bing, bada boom', 'bada boom',
    'bada boom bada bing', 'bah', 'bam', 'banzai', 'bastard', 'batter up',
    'battle stations', 'beauty',
    'because', 'begad', 'begorra', 'begorrah', 'bejeezus', 'bejesus',
    'big deal', 'big whoop',
    'big wow', 'bingo', 'bish bash bosh', 'blah', 'blah blah blah', 'bleah',
    'blech', 'bleeding heck',
    'bleeding hell', 'bleh', 'bless you', 'blimey', "blimey O'Reilly",
    "blimey O'Riley", 'blood and tommy', 'bloody Nora',
    'blooming heck', 'blooming hell', 'blow this for a game of soldiers',
    'bog off', 'bollocks', 'bon voyage', 'boo', 'boo hoo',
    'boom', 'booyah', 'booyakasha', 'bosh', 'bostin', 'bother', 'bottoms up',
    'boutye',
)
# vim:filetype=html
