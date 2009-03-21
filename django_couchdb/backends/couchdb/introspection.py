from django.db.backends import BaseDatabaseIntrospection


__all__ = ('DatabaseIntrospection',)

class DatabaseIntrospection(BaseDatabaseIntrospection):
    """
    @summary: Django CouchDB backend's implementation for Django's
    BaseDatabaseIntrospection class.
    """
    def get_table_list(self, cursor):
        return list(cursor.server.__iter__())

    def get_table_description(self, cursor, table_name):
        return cursor.server[table_name]['_meta']
