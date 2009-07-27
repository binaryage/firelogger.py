from StringIO import StringIO
import nose.tools as NT

from wsgiref.simple_server import demo_app
from webtest import TestApp

import firepython as FPY
import firepython.utils as FU
import firepython._const as FC
import firepython.middleware as FM

try:
    import gprof2dot
except ImportError:
    gprof2dot = None


def test_middleware():
    app = get_app()
    fp = app.app

    yield NT.assert_equal, 'snarf', fp._password, "_password set"
    yield NT.assert_equal, 'itest', fp._logger_name, "_logger_name set"
    yield NT.assert_equal, True, fp._check_agent, "_check_agent set"

    real_stringio = FM.StringIO
    FM.StringIO = MonkeyPatchStringIO
    FM.StringIO.writebuf[:] = []

    filtered_req = app.get('/', extra_environ=get_filterable_env())

    if gprof2dot:
        yield NT.assert_true, bool(FM.StringIO.writebuf), \
            "filtered request writes to StringIO instance"

    FM.StringIO = real_stringio


def get_app():
    app = FM.FirePythonWSGI(demo_app, password='snarf', logger_name='itest')
    app = TestApp(app)
    return app


def get_filterable_env():
    env = {}
    env[FC.FIRELOGGER_PROFILER_ENABLED] = 'yes'
    env[FC.FIRELOGGER_VERSION_HEADER] = FPY.__api_version__
    env[FC.FIRELOGGER_AUTH_HEADER] = FU.get_auth_token('snarf')
    return env


class MonkeyPatchStringIO(StringIO):
    writebuf = []

    def write(self, some_bytes):
        self.writebuf.append(some_bytes)
        StringIO.write(self, some_bytes)
        # ^--- can't use `super` because this is a classobj :(
