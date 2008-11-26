# -*- mode: python; coding: utf-8 -*-
#

try:
    import simplejson
except ImportError:
    from django.utils import simplejson


class TolerantJSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        return str(o)

def json_encode(data):
    return simplejson.dumps(data, cls=TolerantJSONEncoder)
