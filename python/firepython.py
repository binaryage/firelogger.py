# FirePython server-side suport
#
# Depends on simplejson!
# 
# Usage:
#     in all handlers where you want to capture logging ...
#     
#     import firepython
# 
#     # somewhere on the beginning of your response, before any of your logging takes place:
#     handler = firepython.FirePythonLogHandler()
#     root = logging.getLogger()
#     root.addHandler(handler)
#     root.setLevel(logging.DEBUG)
# 
#     # right before serving your response back to server:
#     root.removeHandler(handler)
#     handler.flush(response) # this will add headers into response
#
#  ---- 
#
#  Stay tuned, more docs will hopefully be in the next version.
#
#  Any help with this library would be much appreciated, I'm a Python hater. 
#
#  antonin@hildebrand.cz
#

import sys
import types
import simplejson
import logging
import base64
import time
import traceback

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
        return str(o);
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

    def __init__(self, *arguments, **keywords):
        logging.Handler.__init__(self, *arguments, **keywords)
        self.queue = []
        self._start_time = time.time()

    def emit(self, record):
        self.queue.append(self._prepare_log_record(record))
        
    def _prepare_log_record(self, record):
        data = {
            "level": self._log_level(record.levelno),
            "message": self.format(record),
            "timestamp": long(record.created * 1000 * 1000),
            "time": time.strftime("%H:%M:%S", time.localtime(record.created))+(".%03d" % ((record.created - long(record.created)) * 1000))
        }
        props = ["args", "pathname", "lineno", "exc_info", "exc_text", "name", "process", "thread", "threadName"]
        for p in props:
            try:
                data[p] = record.__dict__[p]
            except:
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
        chunks = data.split("\n")
        return chunks
            
    def flush(self, response):
        if len(self.queue)==0: return
        data = {
            "logs": self.queue,
        }
        chunks = self._encode(data)
        i = 0
        for c in chunks:
            i = i + 1
            response.headers.add_header('FirePython-%d' % i, c)
        self.queue = []
