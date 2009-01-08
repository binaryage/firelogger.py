# -*- mode: python; coding: utf-8 -*-
#
import firepython

try:
    import simplejson
except ImportError:
    from django.utils import simplejson

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class TolerantJSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        return str(o)

def json_encode(data):
    return simplejson.dumps(data, cls=TolerantJSONEncoder)

def get_user_agent(version = firepython.__version__):
    return "X-FirePython/"+version
    
def get_auth_token(password):
    return md5('#FirePythonPassword#%s#' % password).hexdigest()
    
def get_auth_header(password):
    return ("X-FirePythonAuth", get_auth_token(password))