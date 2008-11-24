# Django support for FirePython

import logging
import firepython

class OldStyleHeaders(object):
    """
    Support class for Django's HttpResponse to mimic behavior from 0.96
    """
    def __init__(self, response):
        self.response = response

    def add_header(self, name, value):
        self.response[name] = value

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
        response.headers = OldStyleHeaders(response)
        self.handler.flush(response)
        return response
