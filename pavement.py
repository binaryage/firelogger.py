# -*- coding: utf-8 -*-
import os
import re
import sys

from paver.easy import *
from paver.setuputils import setup, find_packages

ROOT = path.getcwd()
sys.path.insert(0, ROOT) # use firepython from current folder

from firepython._setup_common import SETUP_ARGS

BUILD_DIR = ROOT/'build'
DIST_DIR = ROOT/'dist'
FPY = ROOT/'firepython'
FPY_EGG_INFO = ROOT/'FirePython.egg-info'
CRUFT = [
    BUILD_DIR,
    DIST_DIR,
    FPY_EGG_INFO,
    ROOT/'paver-minilib.zip',
]
API_VERSION = re.compile(r'<em:version>([^<]*)<\/em:version>')
PY_API_VERSION_DEF_RE = re.compile('__api_version__ = [\'"][^\'"]+[\'"]')
PY_API_VERSION_DEF = '__api_version__ = \'%s\''


SETUP_ARGS['packages'] = find_packages(exclude=['tests'])
setup(**SETUP_ARGS)


@task
@needs(['sdist'])
def pypi():
    """Update PyPI index and upload library sources"""
    sh('python setup.py register')
    sh('python setup.py sdist --formats=gztar,bztar,zip upload')

@task
def clean():
    """Clean up generated cruft"""
    for cruft_path in CRUFT:
        if cruft_path.isfile():
            cruft_path.remove()
        elif cruft_path.isdir():
            cruft_path.rmtree()


@task
@needs(['minilib', 'distutils.command.sdist'])
def sdist():
    """Combines paver minilib with setuptools' sdist"""
    pass


_TESTS_INSTALL_PKG = """\
    Tests require `%(mod)s`.
    Please `easy_install` or `pip install` the `%(pkg)s` package'
"""

@task
def _pretest_check():
    had_fail = False

    for mod, pkg in (('mock', 'Mock'), ('webtest', 'WebTest')):
        try:
            import mock
        except ImportError:
            info(_TESTS_INSTALL_PKG % dict(mod=mod, pkg=pkg))
            had_fail = True

    if had_fail:
        raise ImportError


@task
@needs(['_pretest_check', 'setuptools.command.test'])
def test():
    """make sure we have test dependencies, possibly alert user
    about what to do to resolve, then run setuptools' `test`
    """
    pass


@task
def testall():
    """run *all* of the tests (requires nose)"""
    try:
        import nose
    except ImportError:
        info(_TESTS_INSTALL_PKG % dict(mod='nose', pkg='nose'))
        raise

    args = [
        'nosetests',
        '-i',
        '^itest',
        '-v',
        ROOT/'tests',
        '--with-coverage',
        '--cover-package',
        'firepython',
    ]
    nose.run(argv=args)
