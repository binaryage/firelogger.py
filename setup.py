#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

import firepython


SETUP_ARGS = dict(
    name='FirePython',
    version=firepython.__version__,
    description='Python logging console integrated into Firebug',
    long_description=firepython.__doc__,
    author='Antonin Hildebrand',
    author_email='antonin@hildebrand.cz',
    url='http://firepython.binaryage.com',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Logging',
    ],
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False,
)

def main():
    setup(**SETUP_ARGS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
