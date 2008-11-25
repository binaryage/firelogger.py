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
        firepython.install_handler(self.root, self.handler,
                                   request.META['HTTP_USER_AGENT'])

    def process_response(self, request, response):
        firepython.remove_handler(self.root, self.handler,
                                  response.__setitem__)
        return response
