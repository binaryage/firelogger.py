#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup

try:
    from firepython import __version__
except ImportError:
    LINE = '*' * 78
    print >> sys.stderr, LINE
    print >> sys.stderr, """\

    NOT SO FAST:

        If developing firepython from the source checkout,
        one must first run `rake develop`, or simply create
        a `firepython` dir and copy all but this `setup.py`
        python module into it.

    """
    print >> sys.stderr, LINE
    sys.exit(1)


SETUP_ARGS = dict(
    name='firepython',
    version=__version__,
    description='Python logging console integrated into Firebug',
    author='Antonin Hildebrand',
    author_email='antonin@hildebrand.cz',
    url='http://firepython.binaryage.com',
    packages=['firepython'],
    classifiers=['Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Bug Tracking',
                'Topic :: Software Development :: Quality Assurance',
                'Topic :: Software Development :: Testing',
                'Topic :: System :: Logging'],
)

def main():
    setup(**SETUP_ARGS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
