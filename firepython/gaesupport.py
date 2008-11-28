import logging

from google.appengine.ext import webapp

class FirePythonRequestHandler(webapp.RequestHandler):
    """
    This descendant of webapp.RequestHandler allows to proper exception
    catching in FirePython console.
    """
    def handle_exception(self, e, debug_mode):
        self.error(500)
        logging.exception(e)
        if debug_mode:
            import sys, traceback
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(lines)
