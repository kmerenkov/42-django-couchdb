from django.db.backends import BaseDatabaseOperations


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
