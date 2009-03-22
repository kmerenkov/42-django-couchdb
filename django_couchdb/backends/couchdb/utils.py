from time import time
from itertools import izip

import couchdb


__all__ = ('ConnectionWrapper', 'CursorWrapper', 'DatabaseError',
           'DebugCursorWrapper', 'IntegrityError', 'InternalError',
           'SQL', 'Sequence')

DatabaseError = couchdb.ServerError
IntegrityError = couchdb.ResourceConflict

class Sequence(object):
    def __init__(self, server, name):
        if not 'sequences' in server.__iter__():
            table = server.create('sequences')
        else:
            table = server['sequences']

        try:
            seq = table[name]
        except couchdb.ResourceNotFound:
            seq = {'nextval': 1}
        self._nextval = seq['nextval']
        seq['nextval']=seq['nextval'] + 1
        table[name] = seq

    def nextval(self): # doesn't increment
        return self._nextval

    def currval(self):
        return self._nextval - 1

class InternalError(DatabaseError):
    """
    @summary: Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc.
    It must be a subclass of DatabaseError.
    """

def unquote_name(name):
    if name.startswith('"') and name.endswith('"'):
        return name[1:-1]
    return name

class SQL(object):
    def __init__(self, command, params):
        self.command = command
        self.params = params

    def execute_create(self, server):
        # self.params --- (model opts, field_params)
        opts = self.params[0]
        table = server.create(opts.db_table)
        meta = {'_id': '_meta'}
        if opts.unique_together:
            meta['UNIQUE'] = list(opts.unique_together)
        for field, field_params in self.params[1].iteritems():
            params_list = []
            for param, value in field_params.iteritems():
                if value:
                    params_list.append(param)
            meta[field] = params_list
        table['_meta'] = meta

    def execute_add_foreign_key(self, server):
        # self.params - (r_table, r_col, table)
        table = server[self.params[0]]
        meta = table['_meta']
        try:
            refs = meta['REFERENCES']
        except KeyError:
            refs = []
        refs.append('%s=%s' % (self.params[1], self.params[2]))
        meta['REFERENCES'] = refs
        table['_meta'] = meta

    def execute_insert(self, server, params):
        # self.params --- (table name, columns, values)
        table = server[self.params[0]]
        seq = Sequence(server, ("%s_seq"% (self.params[0], )))
        id = str(seq.nextval())
        obj = {'_id': id}
        for key, view, val in izip(self.params[1], self.params[2], params):
            obj[key] = view % val
        table[id] = obj


    def simple_select(self,server, table, columns, where, params):
        def create_where_statement(s, params):
            table_name = unquote_name(s[:s.find('.')])
            field_name = unquote_name(s[s.find('.')+1:s.find(' ')])
            if field_name == 'id':
                field_name = '_id'
            statement = s[s.find(' '):]

            if 'in' in statement: # hack
                params = '{'+','.join('%s: 1' % x for x in params) + '}'
            return ('d.'+field_name + statement) % params

        map_fun = "function (d) { if (d._id!=\"_meta\") {"
        if where:
            st = create_where_statement(where, params)
            map_fun += "if ("+st+") {"

        # just selecting, not where
        map_fun += "result = ["
        str_columns = ','.join(map(lambda x: "d._id" if unquote_name(x.split('.')[1]) == 'id' else
                                "d."+ unquote_name(x.split('.')[1]),
                           (x for x in columns)))
        map_fun += str_columns;
        map_fun += "] ;emit(d._id, result);"
        map_fun += "}}"
        if where:
            map_fun += '}'

        view = table.query(map_fun)
        return view

    def execute_select(self, server, cursor, params):

        # self.params --- (distinct flag, table columns, from, where, extra where,
        #             group by, having, ordering, limits)

        table = server[unquote_name(self.params[2][0])]
        if len(self.params[1])==1 and self.params[1][0]=='COUNT(*)':

            map_fun = "function (d) { if (d._id!=\"_meta\") {emit(null,null);}}"
            cursor.save_one(len(table.query(map_fun)))
        else:
            cursor.save_view(self.simple_select(server, table,
                                           self.params[1], self.params[3], params))

    def execute_delete(self, server, params):
        # self.params ---(table_name, where)
        table_name = self.params[0]
        where = self.params[1]
        table = server[unquote_name(table_name)]
        view = self.simple_select(server, table, (table_name+'.'+'"id"',),
                                  where, params)
        for x in view:
            del table[x.id]

    def execute_sql(self, cursor, params):
        server = cursor.server
        if self.command == 'create':
            return self.execute_create(server)
        elif self.command == 'add_foreign_key':
            return self.execute_add_foreign_key(server)
        elif self.command == 'insert':
            return self.execute_insert(server, params)
        elif self.command == 'select':
            return self.execute_select(server, cursor, params)
        elif self.command == 'delete':
            return self.execute_delete(server, params)

    def __unicode__(self):
        return u"command %s with params = %s" % (self.command, self.params)

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
            sql.execute_sql(self, params)

    def save_view(self, view):
        self.saved_view = view
        self.saved_view_offset = 0

    def save_one(self, one):
        self.saved_one = one

    def fetchone(self):
        return [self.saved_one]

    def fetchmany(self, count):
        ret = list(self.saved_view)[self.saved_view_offset:self.saved_view_offset+count]
        self.saved_view_offset += count
        return map(lambda x:x.value,ret)

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
            print "SQL:", unicode(sql)
            print "PARAMS:", params
            super(DebugCursorWrapper, self).execute(sql, params)
        finally:
            stop = time()
            #~ sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            #~ self.db.queries.append({
                #~ 'sql': sql,
                #~ 'time': "%.3f" % (stop - start),
            #~ })



