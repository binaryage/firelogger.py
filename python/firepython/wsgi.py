# WSGI support for FirePython

import logging
import firepython

class FirePythonWSGI(object):
    """
    WSGI middleware to enable FirePython logging.
    """
    def __init__(self, app):
        self.app = app
        self.handler = firepython.FirePythonLogHandler()
        self.root = logging.getLogger()

    def __call__(self, environ, start_response):
        self.root.addHandler(self.handler)
        self.root.setLevel(logging.DEBUG)

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
        self.root.removeHandler(self.handler)
        self.handler.flush(add_header)

        # start responding
        start_response(*resp_info)
        return output
