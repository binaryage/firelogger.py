import os

from nose import SkipTest
import nose.tools as NT

try:
    from paste.fixture import TestApp
    from paste.deploy import loadapp
except ImportError:
    TestApp = loadapp = None

import firepython as FP
import firepython._const as FPC
import firepython.utils as FPU

try:
    import json
except ImportError:
    import simplejson as json

HERE = os.path.dirname(os.path.abspath(__file__))
INI = os.path.join(HERE, 'test.ini')


def test_paste_integration():
    if None in (TestApp, loadapp):
        def raiser(exc, msg):
            raise exc(msg)
        yield raiser, SkipTest, 'incomplete Paste dependencies, so ' \
                                'not testing Paste integration'
        raise StopIteration
    app = get_app()
    clean_response = app.get('/')
    yield NT.assert_true, bool(clean_response.body)
    yield NT.assert_equal, 1, len(clean_response.headers)

    with_error = app.get('/BORK?error=PLEASE',
                         extra_environ=get_extra_environ(app))
    yield NT.assert_true, len(with_error.headers) >= 226 #TODO improve accuracy
                                                         # of assertion

    firelogger_headers = []
    for assertion in _check_and_gather_headers(with_error,
                                               firelogger_headers):
        yield assertion

    firelogger_headers.sort()
    as_python = _get_headers_as_python(firelogger_headers)
    yield NT.assert_equal, ['logs'], as_python.keys()
    logs = as_python['logs']
    yield NT.assert_equal, 6, len(logs)


def get_app():
    return TestApp('config:%s' % INI)


def get_extra_environ(app):
    ret = {
        FPC.FIRELOGGER_VERSION_HEADER: FP.__api_version__,
    }
    auth_key, auth_value = FPU.get_auth_header(app.app._password)
    ret[auth_key] = auth_value
    return ret


def _check_and_gather_headers(response, out_headers):
    for header, value in response.headers:
        if header.startswith('Fire'):
            index = int(header.split('-')[-1])
            out_headers.append((index, value))
            match = bool(FPC.FIRELOGGER_RESPONSE_HEADER.match(header))
            yield NT.assert_true, match, "header is of correct format"


def _get_headers_as_python(headers):
    decoded = _get_headers_as_string(headers)
    as_python = json.loads(decoded)
    return as_python


def _get_headers_as_string(headers):
    decoded = _get_headers_as_base64(headers).decode('base64')
    return decoded


def _get_headers_as_base64(headers):
    return ''.join([header[1] for header in headers])


EXPECTED_RECORD_KEYS = [
    u'args',
    u'exc_frames',
    u'exc_info',
    u'exc_text',
    u'level',
    u'lineno',
    u'message',
    u'name',
    u'pathname',
    u'process',
    u'template',
    u'thread',
    u'threadName',
    u'time',
    u'timestamp',
]
