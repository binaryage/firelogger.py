import nose.tools as NT


IMPORT_MODS = [
    'firepython',
    'firepython.utils',
    'firepython.middleware',
    'firepython.handlers',
    'firepython._const',
    'firepython._setup_common',
    'firepython.demo',
    'firepython.demo.app',
    'firepython.demo._body',
]


def test_can_import_everything_okay_and_dunder_alls_are_good():
    for mod in IMPORT_MODS:
        imported = __import__(mod, {}, {}, mod.split('.'))

        yield NT.assert_true, bool(imported), \
            "module %s imports okay" % mod

        for member in getattr(imported, '__all__', []):
            yield NT.assert_true, hasattr(imported, member), \
                "module %s has attr %s" % (imported, member)
