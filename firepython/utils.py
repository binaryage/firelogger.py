# -*- mode: python; coding: utf-8 -*-
import sys
from firepython import __api_version__
import firepython._const as CONST


__all__ = [
    'json_encode',
    'get_version_header',
    'get_auth_token',
    'get_auth_header',
]

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

try:
    from hashlib import md5
except ImportError:
    from md5 import md5


class TolerantJSONEncoder(json.JSONEncoder):

    def default(self, o):
        return str(o)


def json_encode(data):
    return json.dumps(data, cls=TolerantJSONEncoder)


def get_version_header(version=__api_version__):
    return (CONST.FIRELOGGER_VERSION_HEADER, version)


def get_auth_token(password):
    return md5(CONST.AUTHTOK_FORMAT % password).hexdigest()


def get_auth_header(password):
    return (CONST.FIRELOGGER_AUTH_HEADER, get_auth_token(password))
