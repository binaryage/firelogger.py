# -*- mode: python; coding: utf-8 -*-

import base64
import logging
import os
import sys
import time
import traceback
import random

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import firepython
import firepython.utils
from firepython.handlers import ThreadBufferedHandler
import jsonpickle

# add a new backed jsonpickle for Django
# jsonpickle will attempt to import this if default jsonpickle libraries are not present
jsonpickle.load_backend('django.utils.simplejson', 'dumps', 'loads', ValueError)


class FirePythonBase(object):

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

    def _version_check(self, version_header):
        version = version_header.strip()
        if version == '':
            # see http://github.com/darwin/firelogger/commit/aaeb68c4034f066e88d206b47b6e0649beadee77
            version = '0.2'
        if firepython.__version__ != version:
            logging.warning('FireLogger has version %s, but FirePython part is %s',
                            version, firepython.__version__)
        return True

    def _password_check(self, token):
        if self._password is None:
            raise Exception("self._password must be set!")
        if not firepython.utils.get_auth_token(self._password) == token:
            logging.warning('FireLogger password does not match. Logging output won\'t be sent to FireLogger. Double check your settings!')
            return False
        return True

    def _check(self, env):
        self._profile_enabled = env.get(firepython.FIRELOGGER_PROFILER_ENABLED, '') != ''
        if (self._check_agent and
            not self._version_check(env.get(firepython.FIRELOGGER_VERSION_HEADER, ''))):
            return False
        if ((self._password and
             not self._password_check(env.get(firepython.FIRELOGGER_AUTH_HEADER, '')))):
            return False
        return True

    def _sanitize_exc_info(self, exc_info):
        if exc_info==None:
            return ("?", "No exception info available", [])
        exc_type = exc_info[0]
        exc_value = exc_info[1]
        exc_traceback = exc_info[2]
        if exc_traceback is not None:
            exc_traceback = traceback.extract_tb(exc_traceback)
        return (exc_type, exc_value, exc_traceback)

    def _handle_internal_exception(self, e):
        if firepython.RAZOR_MODE: # in razor mode hurt web server
            raise e
        # in non-razor mode report internal error to firepython addon
        exc_info = self._sanitize_exc_info(sys.exc_info())
        return {"message": "Internal FirePython error: %s" % unicode(e),
                "exc_info": exc_info}

    def _encode(self, logs, errors=None, profile=None):
        data = {"logs": logs }
        if errors:
            data['errors'] = errors
        if profile:
            data['profile'] = profile
        try:
            data = jsonpickle.encode(data, unpicklable=False,
                                     max_depth=firepython.JSONPICKLE_DEPTH)
        except Exception, e:
            # this exception may be fired, because of buggy __repr__ or
            # __str__ implementations on various objects
            errors = [self._handle_internal_exception(e)]
            try:
                data = jsonpickle.encode({"errors": errors }, unpicklable=False,
                                         max_depth=firepython.JSONPICKLE_DEPTH)
            except Exception, e:
                # even unable to serialize error message
                data = jsonpickle.encode(
                    {"errors": { "message": "FirePython has a really bad day :-(" } },
                    unpicklable=False, max_depth=firepython.JSONPICKLE_DEPTH)
        data = data.encode('utf-8')
        data = base64.encodestring(data)
        return data.splitlines()

    def republish(self, headers):
        firelogger_headers = []
        for key, value in headers.iteritems():
            if firepython.FIRELOGGER_RESPONSE_HEADER.match(key):
                firelogger_headers.append((key, value))

        self._handler.republish(firelogger_headers)

    def _flush_records(self, add_header, profile=None):
        """
        Flush collected logs into response.

        Argument ``add_header`` should be a function receiving two arguments:
        ``name`` and ``value`` of header.
        """

        records = self._handler.get_records()
        self._handler.clear_records()
        republished = self._handler.get_republished()
        self._handler.clear_republished()

        for name, value in republished:
            add_header(name, value)

        logs = []
        errors = []
        for record in records:
            try:
                logs.append(self._prepare_log_record(record))
            except Exception, e:
                # this exception may be fired, because of buggy __repr__ or
                # __str__ implementations on various objects
                errors.append(self._handle_internal_exception(e))

        chunks = self._encode(logs, errors, profile)
        guid = "%08x" % random.randint(0,0xFFFFFFFF)
        for i, chunk in enumerate(chunks):
            add_header('FireLogger-%s-%d' % (guid, i), chunk)

    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": self._handler.format(record),
            "template": record.msg,
            "timestamp": long(record.created * 1000 * 1000),
            "time": (time.strftime("%H:%M:%S", time.localtime(record.created)) +
                     (".%03d" % ((record.created - long(record.created)) * 1000)))
        }
        props = ["args", "pathname", "lineno", "exc_text", "name", "process",
                 "thread", "threadName"]
        for p in props:
            try:
                data[p] = getattr(record, p)
            except AttributeError:
                pass

        try:
            exc_info = getattr(record, 'exc_info')
            if exc_info is not None:
                data['exc_info'] = self._sanitize_exc_info(exc_info)

                frames = []
                t = exc_info[2]
                while t:
                    try:
                        d = {}
                        for k,v in t.tb_frame.f_locals.iteritems():
                            if firepython.DEEP_LOCALS:
                                d[unicode(k)] = v
                            else:
                                d[unicode(k)] = repr(v)
                        frames.append(d)
                    except:
                        frames.append('?')
                    t = t.tb_next
                data['exc_frames'] = frames
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

    def _get_app(self):
        """Returns the WSGI app to run.

        If the FIRELOGGER_PROFILER_ENABLED header has been passed to this WSGI
        request, the returned application will be wrapped with a profiler.
        """
        if not self._profile_enabled:
            return self._app
        try:
            import cProfile as profile
        except ImportError:
            import profile
        self._prof = profile.Profile()
        def prof_wrapper(environ, start_response):
            return self._prof.runcall(self._app, environ, start_response)
        return prof_wrapper

    def _prepare_profile(self):
        """Prepares profiling information."""
        if not self._profile_enabled:
            return None

        try:
          import gprof2dot
        except ImportError:
          logging.error('Unable to profile request: Could not find gprof2dot module')
          return None

        self._prof.create_stats()
        parser = gprof2dot.PstatsParser(self._prof)
        def get_function_name((filename, line, name)):
            module = os.path.splitext(filename)[0]
            module_pieces = module.split(os.path.sep)
            return "%s:%d:%s" % ("/".join(module_pieces[-4:]), line, name)
        parser.get_function_name = get_function_name
        output = StringIO()
        gprof = parser.parse()

        gprof.prune(0.005, 0.001)  # TODO: Parameterize node and edge thresholds.
        dot = gprof2dot.DotWriter(output)
        theme = gprof2dot.TEMPERATURE_COLORMAP
        theme.bgcolor = (0.0, 0.0, 0.0)  # Use black text, for less eye-bleeding.
        dot.graph(gprof, theme)

        def get_info(self):
            s = "Profile Graph:"
            s += " %.3fs CPU" % self.total_tt
            s += ": %d function calls" % self.total_calls
            if self.total_calls != self.prim_calls:
                s += " (%d primitive calls)" % self.prim_calls
            return s

        profile = {
          "producer": "gprof2dot",
          "producerVersion": str(gprof2dot.__version__),
          "info": get_info(parser.stats),
          "dot": output.getvalue(),
        }

        return profile


class FirePythonDjango(FirePythonBase):
    """
    Django middleware to enable FirePython logging.

    To use add 'firepython.django.FirePythonDjango' to your MIDDLEWARE_CLASSES
    setting.

    Optional settings:

     - ``FIREPYTHON_PASSWORD``: password to protect your logs
     - ``FIREPYTHON_LOGGER_NAME``: specific logger name you want to monitor
     - ``FIREPYTHON_CHECK_AGENT``: set to False for prevent server to check
       presence of firepython in user-agent HTTP header.
    """

    def __init__(self):
        from django.conf import settings
        self._password = getattr(settings, 'FIREPYTHON_PASSWORD', None)
        self._logger_name = getattr(settings, 'FIREPYTHON_LOGGER_NAME', None)
        self._check_agent = getattr(settings, 'FIREPYTHON_CHECK_AGENT', True)
        self.install_handler()

    def __del__(self):
        self.uninstall_handler()

    def process_request(self, request):
        if not self._check(request.META):
            return

        self._start()

    def process_response(self, request, response):
        if not self._check(request.META):
            return response

        self._finish()
        self._flush_records(response.__setitem__)
        return response

    def process_exception(self, request, exception):
        if not self._check(request.META):
            return

        logging.exception(exception)


class FirePythonWSGI(FirePythonBase):
    """
    WSGI middleware to enable FirePython logging.

    Supply an application object and an optional password to enable password
    protection. Also logger name may be specified.
    """
    def __init__(self, app, password=None, logger_name=None, check_agent=True):
        self._app = app
        self._password = password
        self._logger_name = logger_name
        self._check_agent = check_agent
        self.install_handler()

    def __del__(self):
        self.uninstall_handler()

    def __call__(self, environ, start_response):
        if not self._check(environ):
            return self._app(environ, start_response)

        # ask why? http://jjinux.blogspot.com/2006/10/python-modifying-counter-in-closure.html
        closure = ["200 OK", [], None]
        sio = StringIO()
        def faked_start_response(_status, _headers, _exc_info=None):
            closure[0] = _status
            closure[1] = _headers
            closure[2] = _exc_info
            return sio.write

        def add_header(name, value):
            closure[1].append((name, value))

        self._start()
        # run app
        try:
            app = self._get_app()
            app_iter = app(environ, faked_start_response)
            output = list(app_iter)
        except Exception:
            logging.exception(sys.exc_info()[1])
            raise
        except:
            logging.warning("DeprecationWarning: raising a string exception is deprecated")
            logging.exception(sys.exc_info()[0])
            raise
        finally:
            # Output the profile first, so we can see any errors in profiling.
            profile = self._prepare_profile()
            self._finish()
            self._flush_records(add_header, profile)

        # start responding
        write = start_response(*closure)
        if sio.tell(): # position is not 0
            sio.seek(0)
            write(sio.read())
        return output
