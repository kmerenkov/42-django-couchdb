import couchdb


__all__ = ('ConnectionWrapper', 'CursorWrapper', 'DatabaseError',
           'DebugCursorWrapper', 'IntegrityError', 'InternalError')

DatabaseError = couchdb.ServerError
IntegrityError = couchdb.ResourceConflict

class InternalError(DatabaseError):
    """
    @summary: Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc.
    It must be a subclass of DatabaseError.
    """

class ConnectionWrapper(object):
    """
    @summary: DB-API 2.0 Connection object for Django CouchDB backend.
    """
    def __init__(self, host, username, password, cache=None, timeout=None):
        self._cursor = None
        self._server = couchdb.Server(host, cache, timeout)
        self._username, self._password = username, password

    def close(self):
        if self._server is not None:
            self._server = None

    def commit(self):
        raise NotImplementedError

    def cursor(self):
        if self._server is None:
            raise InternalError, 'Connection to server was closed.'

        if self._cursor is None:
            self._cursor = CursorWrapper(self._server,
                                         self._username,
                                         self._password)
        return self._cursor

    def rollback(self):
        raise NotImplementedError

class CursorWrapper(object):
    """
    @summary: DB-API 2.0 Cursor object for Django CouchDB backend.
    """
    def __init__(self, server, username=None, password=None):
        assert isinstance(server, couchdb.Server), \
            'Please, supply ``couchdb.Server`` instance as first argument.'

        self.server = server
        self._username, self._password = username, password

class DebugCursorWrapper(CursorWrapper):
    """
    @summary: Special cursor class, that stores all queries to database for
    current session.
    """
    def __init__(self, cursor):
        super(DebugCursorWrapper, self).__init__(cursor.server,
                                                 cursor._username,
                                                 cursor._password)