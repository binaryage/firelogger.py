# -*- mode: python; coding: utf-8 -*-
#

import base64
import logging
import re
import sys
import time
import traceback

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import firepython
from firepython.handlers import ThreadBufferedHandler
from firepython.utils import json_encode

class FirePythonBase(object):
    FIREPYTHON_UA = re.compile(r'\sX-FirePython/(?P<ver>[0-9\.]+)')

    def __init__(self):
        raise NotImplementedError("Must be subclassed")
    
    def install_handler(self):
        logger = logging.getLogger(self._logger_name)
        self._handler = ThreadBufferedHandler()
        logger.addHandler(self._handler)
    
    def uninstall_handler(self):
        if self._handler is None: 
            return
        logger = logging.getLogger(self._logger_name)
        logger.removeHandler(self._handler)
        self._handler = None

    def _ua_check(self, user_agent):
        check = self.FIREPYTHON_UA.search(user_agent)
        if not check:
            return False
        version = check.group('ver')
        if firepython.__version__ != version:
            logging.warning('FireBug part of FirePython is version %s, but Python part is %s', version, firepython.__version__)
        return True

    def _password_check(self, password):
        if self._password is None:
            raise Exception("self._password must be set!")
        return md5('#FirePythonPassword#%s#' % self._password).hexdigest() == password

    def _encode(self, data):
        data = json_encode(data)
        data = data.encode('utf-8')
        data = base64.encodestring(data)
        return data.splitlines()

    def _flush_records(self, add_header):
        """
        Flush collected logs into response.

        Argument ``add_header`` should be a function receiving two arguments:
        ``name`` and ``value`` of header.
        """

        records = self._handler.get_records()
        self._handler.clear_records()
        logs = []
        for record in records:
            logs.append(self._prepare_log_record(record))

        chunks = self._encode({"logs": logs})
        for i, chunk in enumerate(chunks):
            add_header('FirePython-%d' % i, chunk)

    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": self._handler.format(record),
            "template": record.msg,
            "timestamp": long(record.created * 1000 * 1000),
            "time": (time.strftime("%H:%M:%S", time.localtime(record.created)) +
                     (".%03d" % ((record.created - long(record.created)) * 1000)))
        }
        props = ["args", "pathname", "lineno", "exc_text", "name", "process", "thread", "threadName"]
        for p in props:
            try:
                data[p] = getattr(record, p)
            except AttributeError:
                pass
           
        try:
            exc_info = getattr(record, 'exc_info')
            if exc_info is not None:
                exc_type = exc_info[0]
                exc_value = exc_info[1]
                exc_traceback = exc_info[2]
                if exc_traceback is not None:
                    exc_traceback = traceback.extract_tb(exc_traceback)
                data['exc_info'] = (exc_type, exc_value, exc_traceback)
        except AttributeError:
            pass
        return data

    def _log_level(self, level):
        if level >= logging.CRITICAL:
            return "critical"
        elif level >= logging.ERROR:
            return "error"
        elif level >= logging.WARNING:
            return "warning"
        elif level >= logging.INFO:
            return "info"
        else:
            return "debug"

    def _start(self):
        self._handler.start()

    def _finish(self):
        self._handler.finish()


class FirePythonDjango(FirePythonBase):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.django.FirePythonDjango' to your MIDDLEWARE_CLASSES
    setting.

    Optional settings:
    Set ``FIREPYTHON_PASSWORD`` setting to some password to protect your logs with password.
    Set ``FIREPYTHON_LOGGER_NAME`` to specific logger name you want to monitor.
    """

    def __init__(self):
        from django.conf import settings
        self._password = getattr(settings, 'FIREPYTHON_PASSWORD', None)
        self._logger_name = getattr(settings, 'FIREPYTHON_LOGGER_NAME', None)
        self.install_handler()
        
    def __del__(self):
        self.uninstall_handler()

    def process_request(self, request):
        if not self._ua_check(request.META.get('HTTP_USER_AGENT', '')):
            return

        if (self._password and
            not self._password_check(request.META.get('HTTP_X_FIREPYTHONAUTH', ''))):
            return

        self._start()

    def process_response(self, request, response):
        if not self._ua_check(request.META.get('HTTP_USER_AGENT', '')):
            return response
        if (self._password and
            not self._password_check(request.META.get('HTTP_X_FIREPYTHONAUTH', ''))):
            return response

        self._finish()
        self._flush_records(response.__setitem__)
        return response

    def process_exception(self, request, exception):
        if not self._ua_check(request.META.get('HTTP_USER_AGENT', '')):
            return response
        if (self._password and
            not self._password_check(request.META.get('HTTP_X_FIREPYTHONAUTH', ''))):
            return response

        logging.exception(exception)


class FirePythonWSGI(FirePythonBase):
    """
    WSGI middleware to enable FirePython logging.

    Supply an application object and an optional password to enable password
    protection. Also logger name may be specified.
    """
    def __init__(self, app, password=None, logger_name=None):
        self._app = app
        self._password = password
        self._logger_name = logger_name
        self.install_handler()

    def __del__(self):
        self.uninstall_handler()
        
    def __call__(self, environ, start_response):
        process = (self._ua_check(environ.get('HTTP_USER_AGENT', '')) and
                   not (self._password and
                        not self._password_check(environ.get('HTTP_X_FIREPYTHONAUTH', ''))))

        if not process:
            return self._app(environ, start_response)

        # collect headers
        status = "200 OK"
        headers = []
        exc_info = None
        sio = StringIO()
        def faked_start_response(_status, _headers, _exc_info=None):
            status = _status
            headers = _headers
            exc_info = _exc_info
            return sio.write

        def add_header(name, value):
            headers.append((name, value))

        self._start()
        # run app
        try:
            app_iter = self._app(environ, faked_start_response)
            output = list(app_iter)
        except Exception:
            logging.exception(sys.exc_info()[1])
            raise
        except:
            logging.warning("DeprecationWarning: raising a string exception is deprecated")
            logging.exception(sys.exc_info()[0])
            raise
        finally:
            self._finish()
            self._flush_records(add_header)

        # start responding
        write = start_response(status, headers, exc_info)
        if sio.tell(): # position is not 0
            sio.seek(0)
            write(sio.read())
        return output
