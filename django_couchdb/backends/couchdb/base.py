"""
CouchDB backend for Django.

Requires couchdb Python library (http://couchdb-python.googlecode.com/).
"""

from django.core.exceptions import ImproperlyConfigured
from django.db.backends import *

try:
    import couchdb
except ImportError, e:
    raise ImproperlyConfigured, 'Error loading "couchdb" module: %s' % e


from creation import *
from introspection import *
from operations import *
from utils import *

class DatabaseFeatures(BaseDatabaseFeatures):
    """
    @summary: Database features of Django CouchDB backend.
    """
    can_use_chunked_reads = False
    needs_datetime_string_cast = False
    update_can_self_select = False
    uses_custom_query_class = True

class DatabaseWrapper(BaseDatabaseWrapper):
    #~ operators = {}
    """
    @summary: Database wrapper for Django CouchDB backend.
    """
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.creation = DatabaseCreation(self)
        self.features = DatabaseFeatures()
        self.introspection = DatabaseIntrospection(self)
        self.ops = DatabaseOperations()
        self.validation = BaseDatabaseValidation()

    def _cursor(self, settings):
        if self.connection is None:
            if not settings.DATABASE_HOST:
                raise ImproperlyConfigured, \
                      'Please, fill out DATABASE_HOST in the settings module ' \
                      'before using the database.'
            self.connection = ConnectionWrapper(settings.DATABASE_HOST,
                                                settings.DATABASE_USER,
                                                settings.DATABASE_PASSWORD)
        return self.connection.cursor()

    def make_debug_cursor(self, cursor):
        return DebugCursorWrapper(cursor)


