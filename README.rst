==============
django-couchdb
==============

1. Introduction_
2. Requirements_
3. Installation_
4. Others_

Introduction
============

**django-couchdb** is the Django_ database adapter for CouchDB_ databases.

.. _Django: http://www.djangoproject.com/
.. _CouchDB: http://couchdb.apache.org/

Requirements
============

- Django >= 1.0
- `couchdb-python`_

.. _`couchdb-python`: http://couchdb-python.googlecode.com/

Installation
============

To use this adapter in your Django project:

- Add ``django_couchdb`` directory to ``PYTHONPATH`` environment variable or
  ``sys.path``.

- Set::

    DATABASE_ENGINE = 'django_couchdb.backends.couchdb'

  in your project settings module.

- That's all.

Others
======

;)

