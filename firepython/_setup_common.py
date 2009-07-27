import firepython


SETUP_ARGS = dict(
    name='FirePython',
    version=firepython.__version__,
    description='Python logging console integrated into Firebug',
    long_description=firepython.__doc__,
    author='Antonin Hildebrand',
    author_email='antonin@hildebrand.cz',
    url='http://firepython.binaryage.com',
    packages=['firepython'],
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
    install_requires=['jsonpickle'],
    extras_require={
        'gprof2dot': ['gprof2dot'],
    },
    test_suite='nose.collector',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'firepython-demo-app = firepython.demo:main',
        ],
    }
)
