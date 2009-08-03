#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'django-couchdb',
    version = '',

    description = 'django couchdb app',
    long_description = 'django-couchdb is the Django database adapter for '\
                       'CouchDB databases.',
    author = '42',
    author_email = '',
    license = '',
    url = 'http://trac.khavr.com/project/django-couchdb',

    classifiers = [
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(),
        
    zip_safe = False,

    install_requires = [
        'couchdb-python'
    ],
    
    test_suite='tests',
)
