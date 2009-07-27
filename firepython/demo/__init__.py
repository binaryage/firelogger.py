import sys
import optparse
from wsgiref.simple_server import make_server

from firepython.demo.app import FirePythonDemoApp, LOGGER_NAME
from firepython.middleware import FirePythonWSGI

USAGE = """%prog [options]
serve a demo WSGI application wrapped with FirePython middleware
"""
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 9292
OPTIONS = (
    (('-H', '--host'),
        dict(dest='host', action='store', default=DEFAULT_HOST,
             help='host on which to serve, default=%r' % DEFAULT_HOST)),
    (('-P', '--port'),
        dict(dest='port', action='store', type='int', default=DEFAULT_PORT,
             help='port on which to serve, default=%r' % DEFAULT_PORT)),
    (('-p', '--password'),
        dict(dest='password', action='store', default=None,
             help='password to use for the password protection feature, '
                  'if desired.')),
    (('-X', '--no-check-agent'),
        dict(dest='no_check_agent', action='store_true', default=False,
             help='force *no* checking of User Agent (more permissive), '
                  'default=False')),
)


def main(sysargs=sys.argv[:]):
    parser = optparse.OptionParser(usage=USAGE)
    for args, kwargs in OPTIONS:
        parser.add_option(*args, **kwargs)
    opts = parser.parse_args(sysargs[1:])[0]
    return serve_demo(host=opts.host, port=opts.port,
                      password=opts.password,
                      check_agent=(not opts.no_check_agent))


def serve_demo(host=DEFAULT_HOST, port=DEFAULT_PORT,
               password=None, check_agent=True):
    app = demo_app = FirePythonDemoApp({})
    app = FirePythonWSGI(app, password=password, logger_name=LOGGER_NAME,
                         check_agent=check_agent)
    server = make_server(host, port, app)

    try:
        print "Serving %s(%r) on host=%r, port=%r" % \
            (FirePythonWSGI.__name__, demo_app, host, port)
        server.serve_forever()
    except KeyboardInterrupt:
        return 0

    return 1


def paste_app_factory(global_config, **local_config):
    return FirePythonDemoApp(global_config)


if __name__ == '__main__':
    sys.exit(main())
