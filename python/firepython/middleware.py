import logging
import firepython
from django.conf import settings


class FirePythonDjango(object):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.django.FirePythonDjango' to your MIDDLEWARE_CLASSES
    setting.

    Set ``FIREPYTHON_PASSWORD`` setting to some password to protect your logs
    with password.
    """
    def __init__(self):
        self.handler = firepython.FirePythonLogHandler()
        self.root = logging.getLogger()
        self.password = getattr(settings, 'FIREPYTHON_PASSWORD', None)

    def process_request(self, request):
        firepython.install_handler(
            self.root, self.handler, request.META['HTTP_USER_AGENT'],
            self.password, request.META.get('X-FirePythonAuth', ''))

    def process_response(self, request, response):
        firepython.remove_handler(self.root, self.handler,
                                  response.__setitem__)
        return response


class FirePythonWSGI(object):
    """
    WSGI middleware to enable FirePython logging.

    Supply an application object and an optional password to enable password
    protection.
    """
    def __init__(self, app, password=None):
        self.app = app
        self.handler = firepython.FirePythonLogHandler()
        self.root = logging.getLogger()
        self.password = password

    def __call__(self, environ, start_response):
        firepython.install_handler(
            self.root, self.handler, environ['HTTP_USER_AGENT'],
            self.password, environ.get('X-FirePythonAuth', ''))

        # collect headers
        resp_info = []
        def faked_start_response(status, headers, exc_info=None):
            resp_info.append(status)
            resp_info.append(headers)
            resp_info.append(exc_info)

        # run app
        app_iter = self.app(environ, faked_start_response)
        output = list(app_iter)

        # collect logs
        def add_header(name, value):
            resp_info[1].append((name, value))

        firepython.remove_handler(self.root, self.handler, add_header)

        # start responding
        start_response(*resp_info)
        return output
