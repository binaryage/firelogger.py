#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='firepython',
      version='0.2',
      description='Python logging to Firebug',
      author='Antonin Hildebrand',
      author_email='antonin@hildebrand.cz',
      url='http://github.com/woid/firepython',
      packages=['firepython'],
      install_requires=['simplejson'],
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
