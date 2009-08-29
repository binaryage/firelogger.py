import random
import urllib
import logging
from xml.sax import saxutils
from wsgiref.util import setup_testing_defaults

from firepython.demo._body import BODY, EXCLAMATIONS

LOGGER_NAME = __name__


class FirePythonDemoApp(object):
    _did_setup_logging = False

    def __init__(self, global_config=None):
        if not global_config:
            global_config = {}
        self.global_config = global_config
        self.__body__ = BODY
        self.log = logging.getLogger(LOGGER_NAME)

    def _setup_logging(self):
        if self._did_setup_logging:
            return

        self.log.setLevel(logging.DEBUG)

        for handler in self.log.root.handlers + self.log.handlers:
            handler.setLevel(logging.DEBUG)

        self._did_setup_logging = True

    def __call__(self, environ, start_response):
        self._setup_logging()
        if 'error' in environ.get('QUERY_STRING', '').lower():
            try:
                busted = 10000 / 0
            except Exception:
                self.log.exception('OMG you cannot has division by zero!: ')
                self.log.critical('It is because the Zero cannot be divided!')
                self.log.error('and if you continue to WANT, will be ERROR')
                self.log.warn('I am givin you dis warning!')
                self.log.info('It is for your information')
                self.log.debug('While this is just a bonus')
        else:
            self.log.info('Nothing to see here, folks')
            self.log.debug('for serious ... is nothing')

        start_response('200 OK', [('content-type', 'text/html')])
        body = self.__body__ % dict(
                environ='\n' + self._get_pretty_environ(environ),
                error=urllib.quote(random.choice(EXCLAMATIONS)),
        )
        return [body]

    def _get_pretty_environ(self, environ):
        base = {'QUERY_STRING': ''}

        setup_testing_defaults(base)
        for key in base.keys():
            base[key] = environ.get(key, base[key])

        sortkeys = base.keys()
        sortkeys.sort()

        ret = []
        for key in sortkeys:
            escaped = saxutils.escape(repr(base[key]))
            ret.append('%s: %s\n' % (key, escaped))

        return ''.join(ret)
