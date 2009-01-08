#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

from firepython import __version__

setup(name='firepython',
      version=__version__,
      description='Python logging to Firebug',
      author='Antonin Hildebrand',
      author_email='antonin@hildebrand.cz',
      url='http://github.com/darwin/firepython',
      packages=['firepython'],
      classifiers=['Development Status :: 3 - Alpha',
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
