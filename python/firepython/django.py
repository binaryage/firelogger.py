# Django support for FirePython

import logging
import firepython

class FirePythonDjango(object):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.django.FirePythonDjango' to your MIDDLEWARE_CLASSES
    setting.
    """
    def __init__(self):
        self.handler = firepython.FirePythonLogHandler()
        self.root = logging.getLogger()

    def process_request(self, request):
        self.root.addHandler(self.handler)
        self.root.setLevel(logging.DEBUG)

    def process_response(self, request, response):
        self.root.removeHandler(self.handler)
        self.handler.flush(response.__setitem__)
        return response
