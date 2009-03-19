from django.db.backends import BaseDatabaseIntrospection


__all__ = ('DatabaseIntrospection',)

class DatabaseIntrospection(BaseDatabaseIntrospection):
    """
    @summary: Django CouchDB backend's implementation for Django's
    BaseDatabaseIntrospection class.
    """
    def get_table_list(self, cursor):
        return cursor.server.__iter__()
