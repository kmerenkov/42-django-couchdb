from django.db.backends import BaseDatabaseOperations
from utils import *
from queries import *

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
        s = Sequence(cursor.server, '%s_seq' % (table_name, ))
        return s.currval()

    def query_class(self, DefaultQueryClass):
        class CustomQuery(DefaultQueryClass):
            def __new__(cls, *args, **kwargs):
                if cls.__name__ == 'InsertQuery':
                    NewInsertQuery = get_insert_query(cls)
                    obj =  super(CustomQuery, NewInsertQuery).__new__(NewInsertQuery, *args, **kwargs)
                else:
                    obj =  super(CustomQuery, cls).__new__(cls, *args, **kwargs)
                return obj
        return CustomQuery

