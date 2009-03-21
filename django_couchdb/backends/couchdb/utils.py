from time import time

import couchdb


__all__ = ('ConnectionWrapper', 'CursorWrapper', 'DatabaseError',
           'DebugCursorWrapper', 'IntegrityError', 'InternalError',
           'SQL')

DatabaseError = couchdb.ServerError
IntegrityError = couchdb.ResourceConflict

class InternalError(DatabaseError):
    """
    @summary: Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc.
    It must be a subclass of DatabaseError.
    """

class SQL(object):
    def __init__(self, command, params):
        self.command = command
        self.params = params

    def execute_create(self, server):
        # params --- (table_name, field_params)
        table = server.create(self.params[0])
        meta = {'_id': '_meta'}
        for field, field_params in self.params[1].iteritems():
            params_list = []
            for param, value in field_params.iteritems():
                if value:
                    params_list.append(param)
            meta[field] = params_list
        table['_meta'] = meta

    def execute_add_foreign_key(self, server):
        # params - (r_table, r_col, table)

        table = server[self.params[0]]
        meta = table['_meta']
        try:
            refs = meta['REFERENCES']
        except KeyError:
            refs = []
        refs.append('%s=%s' % (self.params[1], self.params[2]))
        meta['REFERENCES'] = refs

    def execute_sql(self, server, params):
        if self.command == 'create':
            return self.execute_create(server)
        elif self.command == 'add_foreign_key':
            return self.execute_add_foreign_key(server)

    def __unicode__(self):
        return u"%s on %s with %s" % (self.command, self.server, self.params)

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
        #~ raise NotImplementedError
        pass

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

    def execute(self, sql, params=()):
        if isinstance(sql, SQL):
            sql.execute_sql(self.server, params)

class DebugCursorWrapper(CursorWrapper):
    """
    @summary: Special cursor class, that stores all queries to database for
    current session.
    """
    def __init__(self, cursor):
        super(DebugCursorWrapper, self).__init__(cursor.server,
                                                 cursor._username,
                                                 cursor._password)

    def execute(self, sql, params=()):
        start = time()
        try:
            super(DebugCursorWrapper, self).execute(sql, params)
        finally:
            stop = time()
            #~ sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            #~ self.db.queries.append({
                #~ 'sql': sql,
                #~ 'time': "%.3f" % (stop - start),
            #~ })

