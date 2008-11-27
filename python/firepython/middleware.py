# -*- mode: python; coding: utf-8 -*-
#

import base64
import logging
import re
import sys
import time

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


rootLogger = logging.getLogger()
rootLogger.setLevel(logging.NOTSET)
handler = ThreadBufferedHandler()
rootLogger.addHandler(handler)


class FirePythonBase(object):
    FIREPYTHON_UA = re.compile(r'\sX-FirePython/(?P<ver>[0-9\.]+)')

    def __init__(self):
        raise NotImplementedError("Must be subclassed")

    def _ua_check(self, user_agent):
        check = self.FIREPYTHON_UA.search(user_agent)
        if not check:
            return False
        version = check.group('ver')
        if firepython.__version__ != version:
            logging.warning('FireBug part of FirePython is version %s, but Python part is %s', version, __version__)
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

        records = handler.get_records()
        handler.clear_records()
        logs = []
        for record in records:
            logs.append(self._prepare_log_record(record))

        chunks = self._encode({"logs": logs})
        for i, chunk in enumerate(chunks):
            add_header('FirePython-%d' % i, chunk)

    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": handler.format(record),
            "timestamp": long(record.created * 1000 * 1000),
            "time": (time.strftime("%H:%M:%S", time.localtime(record.created)) +
                     (".%03d" % ((record.created - long(record.created)) * 1000)))
        }
        props = ["args", "pathname", "lineno", "exc_info", "exc_text", "name", "process", "thread", "threadName"]
        for p in props:
            try:
                data[p] = getattr(record, p)
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


class FirePythonDjango(FirePythonBase):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.django.FirePythonDjango' to your MIDDLEWARE_CLASSES
    setting.

    Set ``FIREPYTHON_PASSWORD`` setting to some password to protect your logs
    with password.
    """

    def __init__(self):
        from django.conf import settings
        self._password = getattr(settings, 'FIREPYTHON_PASSWORD', None)

    def process_request(self, request):
        if not self._ua_check(request.META.get('HTTP_USER_AGENT', '')):
            return

        if (self._password and
            not self._password_check(request.META.get('HTTP_X_FIREPYTHONAUTH', ''))):
            return

        handler.clear_records()

    def process_response(self, request, response):
        if not self._ua_check(request.META.get('HTTP_USER_AGENT', '')):
            return response
        if (self._password and
            not self._password_check(request.META.get('HTTP_X_FIREPYTHONAUTH', ''))):
            return response

        self._flush_records(response.__setitem__)
        return response

    def process_exception(self, request, exception):
        logging.exception(exception)


class FirePythonWSGI(FirePythonBase):
    """
    WSGI middleware to enable FirePython logging.

    Supply an application object and an optional password to enable password
    protection.
    """
    def __init__(self, app, password=None):
        self._app = app
        self._password = password

    def __call__(self, environ, start_response):
        # collect headers
        resp_info = []
        sio = StringIO()
        def faked_start_response(status, headers, exc_info=None):
            resp_info.append(status)
            resp_info.append(headers)
            resp_info.append(exc_info)
            return sio.write

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

        # collect logs
        def add_header(name, value):
            resp_info[1].append((name, value))

        if (self._ua_check(environ.get('HTTP_USER_AGENT', '')) and
            not (self._password and
                 not self._password_check(environ.get('HTTP_X_FIREPYTHONAUTH', '')))):
            self._flush_records(add_header)

        # start responding
        write = start_response(*resp_info)
        if sio.tell(): # position is not 0
            sio.seek(0)
            write(sio.read())
        return output
