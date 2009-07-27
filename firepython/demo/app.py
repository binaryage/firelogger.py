import random
import logging
from xml.sax import saxutils
from wsgiref.util import setup_testing_defaults

from firepython.demo._body import BODY, EXCLAMATIONS


class FirePythonDemoApp(object):

    def __init__(self, global_config):
        self.global_config = global_config
        self.log = logging.getLogger(__name__)
        self.__body__ = BODY

    def __call__(self, environ, start_response):
        if 'error' in environ.get('QUERY_STRING', '').lower():
            try:
                busted = 10000 / 0
            except Exception:
                self.log.exception('OMG you cannot has division by zero!: ')
        else:
            self.log.info('Nothing to see here, folks')

        start_response('200 OK', [('content-type', 'text/html')])
        body = self.__body__ % dict(
                environ='\n' + self._get_pretty_environ(environ),
                error=random.choice(EXCLAMATIONS)
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
