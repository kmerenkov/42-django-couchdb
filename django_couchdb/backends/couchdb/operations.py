from django.db.backends import BaseDatabaseOperations
from utils import *

__all__ = ('DatabaseOperations',)

class DatabaseOperations(BaseDatabaseOperations):
    """
    @summary: Django CouchDB backend's implementation for Django's
    BaseDatabaseOperations class.
    """
    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name # Quoting once is enough.
        return '"%s"' % name

    def last_insert_id(self, cursor, table_name, pk_name):
        s = Sequence(cursor.server, '%s_%s_seq' % (table_name, pk_name))
        return s.currval()

