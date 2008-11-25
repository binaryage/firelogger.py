# FirePython server-side support library
#
# for usage see README.markdown or http://github.com/woid/firepython
#

import sys
import types
import simplejson
import logging
import base64
import time
import traceback
import re
import threading

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

__version__ = '0.2'

def correctCurrentframe():
    try:
        raise Exception
    except:
        return sys.exc_traceback.tb_frame.f_back.f_back.f_back.f_back # wtf?

# needed to fix pathname inside log records, is this broken in python2.5 on OSX?
logging.currentframe = correctCurrentframe

# TODO: make JSON encoder smart to encode "unknown" structures by sniffing using reflection
class TolerantJSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        return str(o)
        #return super(DateTimeAwareJSONEncoder, self).default(o)

def firepython_json_encode(data, **kwargs):
    def _any(data):
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        else:
            ret = data
        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret

    ret = _any(data)
    return simplejson.dumps(ret, cls=TolerantJSONEncoder)

class FirePythonLogHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.local = threading.local()
        self._start_time = time.time()

    def emit(self, record):
        if not hasattr(self.local, 'queue'):
            self.local.queue = []
        self.local.queue.append(self._prepare_log_record(record))

    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": self.format(record),
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

    def _encode(self, data):
        data = firepython_json_encode(data)
        data = data.encode('utf-8')
        data = base64.encodestring(data)
        return data.splitlines()

    def flush(self, add_header):
        """
        Flush collected logs in response.

        Argument ``add_header`` should be a function receiving two arguments:
        ``name`` and ``value`` of header.
        """
        if getattr(self.local, 'queue', None) is None:
            return
        chunks = self._encode({"logs": self.local.queue})
        for i, chunk in enumerate(chunks):
            add_header('FirePython-%d' % i, chunk)
        self.local.queue = []


FIREPYTHON_UA = re.compile(r'\sX-FirePython/(?P<ver>[0-9\.]+)')

def install_handler(logger, handler, user_agent, password, auth):
    check = FIREPYTHON_UA.search(user_agent)
    if not check:
        return
    if (password and
        md5.new('#FirePythonPassword#%s#' % password).hexdigest() != auth):
        return
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    version = check.group('ver')
    if version != __version__:
        logging.debug('FireBug part of FirePython is version %s, but Python part is %s' %
                      (version, __version__))

def remove_handler(logger, handler, add_header):
    if handler in logger.handlers:
        logger.removeHandler(handler)
        handler.flush(add_header)

