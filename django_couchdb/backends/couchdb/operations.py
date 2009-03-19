from django.db.backends import BaseDatabaseOperations


__all__ = ('DatabaseOperations',)

class DatabaseOperations(BaseDatabaseOperations):
    """
    @summary: Django CouchDB backend's implementation for Django's
    BaseDatabaseOperations class.
    """
