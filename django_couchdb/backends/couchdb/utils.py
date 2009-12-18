from time import time
from itertools import izip
from nodes import Lookup
from model_meta import ModelMeta
import couchdb
from django.conf import settings


__all__ = ('ConnectionWrapper', 'CursorWrapper', 'DatabaseError',
           'DebugCursorWrapper', 'IntegrityError', 'InternalError',
           'SQL', 'Sequence')

DatabaseError = couchdb.client.ServerError
IntegrityError = couchdb.client.ResourceConflict


# FIXME feel free to remove me :)
META_KEY = 'meta'


FAKE_MODELS = settings.FAKE_MODELS


class Sequence(object):
    def __init__(self, server, name):
        if not settings.DATABASE_NAME in server:
            table = server.create(settings.DATABASE_NAME)
        else:
            table = server[settings.DATABASE_NAME]

        table_name = "sequence:%s" % name
        try:
            seq = table[table_name]
        except couchdb.ResourceNotFound:
            seq = {'nextval': 1}
        self._nextval = seq['nextval']
        seq['nextval'] = seq['nextval'] + 1
        seq['Type'] = 'model_sequence'
        table[table_name] = seq

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

def is_fake(name):
    if unquote_name(name) in FAKE_MODELS:
        return True
    return False


WHERE_REPLACEMENTS = {'AND': '&&', 'OR': '||', 'NOT': '!'}

def process_where(where):
    for key, val in WHERE_REPLACEMENTS.iteritems():
        where = where.replace(key, val) # it is dangerous !!!
    return where

def process_views(meta, columns, views):
    for column, view in izip(columns, views):
        options = meta.get(column, [])
        if 'BOOLEAN' in options:
            yield '__RAW__'
        else:
            yield view

class SQL(object):
    def __init__(self, command, params):
        self.command = command
        self.params = params

    def execute_create(self, server):
        # self.params --- (model opts, field_params)
        opts = self.params[0]
        if is_fake(opts.db_table):
            print "%s is fake, skipping create" % opts.db_table
            return
        meta = {}
        if opts.unique_together:
            meta['UNIQUE'] = list(opts.unique_together)
        for field, field_params in self.params[1].iteritems():
            params_list = []
            for param, value in field_params.iteritems():
                if value:
                    params_list.append(param)
            meta[field] = params_list
        model_meta = ModelMeta(server, opts.db_table)
        model_meta.set_meta(meta)
        # FIXME remove me
        # Creating database to not to break selects/inserts/whatever
        # temporary solution :)
        server.create(opts.db_table)

    def execute_add_foreign_key(self, server):
        # self.params - (r_table, r_col, table)
        if is_fake(self.params[0]):
            print "%s is fake, skipping foreign key" % self.params[0]
            return
        model_meta = ModelMeta(server, self.params[0])
        meta = model_meta.get_meta()
        try:
            refs = meta['REFERENCES']
        except KeyError:
            refs = []
        refs.append('%s=%s' % (self.params[1], self.params[2]))
        meta['REFERENCES'] = refs
        model_meta.update_meta(meta)

    def execute_insert(self, server, params):
        # self.params --- (table name, columns, values)
        table_name = self.params[0]
        if is_fake(table_name):
            print "%s is fake, skipping insert" % self.params[0]
            return
        table = server[table_name]
        if not 'id' in self.params[1]:
            seq = Sequence(server, table_name)
            id = str(seq.nextval())
            obj = {'_id': '%s:%s' % (table_name, id)}
        else:
            obj = {}

        model_meta = ModelMeta(server, self.params[0])
        views = process_views(model_meta.get_meta(), self.params[1], self.params[2])
        for key, view, val in izip(self.params[1], views, params):
            if key == 'id':
                key = '_id'
                val = "%s:%s" % (table_name, val)
            if view == '__RAW__':
                obj[key] = val
            else:
                obj[key] = view % val
        table[obj['_id']] = obj

    def execute_update(self, server, params):
        # self.params --- (table name, column-values, where)
        table_name = self.params[0]
        if is_fake(table_name):
            print "%s is fake, skipping update" % table_name
            return
        table = server[table_name]
        view = self.simple_select(server, table, (table_name+'.'+'"id"',),
                                  self.params[2], params)
        columns, values, views = [], [], []
        for col,val,v in self.params[1]:
            columns.append(unquote_name(col))
            values.append(val)
            views.append(v)
        model_meta = ModelMeta(server, self.params[0])
        views = process_views(model_meta.get_meta(), columns, views)
        for d in view:
            obj = table[d.id]
            for key, view, val in izip(columns, views, values):
                if key=='id':
                    key = '_id'
                    val = "%s:%s" % (table_name, val)
                if view == '__RAW__':
                    obj[key] = val
                else:
                    obj[key] = view % val
            table[obj['_id']] = obj

    def simple_select(self, _server, table, columns, where, _params, alias = None):
        if alias:
            table_name = alias
        else:
            table_name = table.name
        if is_fake(table_name):
            print "%s is fake, returning custom data" % table_name
            return FAKE_MODELS[table_name].get()
        map_fun = "function ("+table_name+") { var _d = " + table_name+ ";"
        map_fun += "if ("+table_name+"._id!=\""+META_KEY+"\") {" # FIXME no need in META_KEY here
        if where:
            map_fun += "if ("+process_where(where)+") {"

        # just selecting, not where
        map_fun += "result = ["
        processed_columns = []
        for x in columns:
            if 'AS' in x:
                x = x[:x.find('AS')]
            if '.' in x: # bad usage. Dot can occur in arithmetic operations!!!
                left, right = x.split('.')
                left = unquote_name(left)
                right = unquote_name(right)
                if right=='id':
                    right = '_id'
                if left==table_name:
                    if right=='_id':
                        processed_columns.append('parseInt('+left + '.' + right+')')
                    else:
                        processed_columns.append(left + '.' + right)
            else:
                processed_columns.append(x)
        str_columns = ','.join(processed_columns)
        map_fun += str_columns;
        map_fun += "] ;emit("+table_name+"._id, result);"
        map_fun += "}}"
        if where:
            map_fun += '}'
        # print "MAP_FUN:", map_fun
        view = table.query(map_fun)
        return view

    def execute_simple_select(self, server, cursor, params):
        # self.params --- (distinct flag, table columns, from, where, extra where,
        #             group by, having, ordering, limits)
        table_name = self.params[2][0]
        table = server[unquote_name(table_name)]
        if len(self.params[1])==1 and self.params[1][0]=='COUNT(*)':
            view = self.simple_select(server, table,
                                      (table_name+'.'+'"id"',), self.params[3], params)
            cursor.save_one(len(view))
        else:
            cursor.save_view(self.simple_select(server, table,
                                           self.params[1], self.params[3], params))


    def execute_select(self, server, cursor, params):
        # self.params --- (distinct flag, table columns, from, where, extra where,
        #             group by, having, ordering, limits)
        if is_fake(self.params[2][0]):
            print "%s is fake, returning custom data" % self.params[2][0]
            table_name = unquote_name(self.params[2][0])
            custom_data = FAKE_MODELS[table_name].get()
            if len(self.params[1]) == 1 and self.params[1][0] == 'COUNT(*)':
                cursor.save_one(len(custom_data))
            else:
                cursor.save_view(custom_data)
            return
        else:
            print "ALARM %s" % self.params[2][0]
        if len(self.params[2]) == 1:
            return self.execute_simple_select(server,cursor,params)
        else:
            leftmost_table_name = self.params[2][0]
            lookups = []
            for x in self.params[2][1:]:
                left, right = x.split('ON')
                left = left.split()
                right = right[2:-1].split()
                if left[0] == 'INNER':
                    if len(left) == 4: # in case of alias
                        table_name = left[2]
                        alias = left[3]
                    else:
                        table_name = left[2]
                        alias = unquote_name(left[2])
                    table = server[unquote_name(table_name)]
                    view = self.simple_select(server, table,
                                              (table_name+'.'+'"id"',),
                                              self.params[3], params, alias=alias)
                    ids = (d.id for d in view)
                    # table_alias, name, db_type, lookup_type, value_annot, params
                    l = Lookup(leftmost_table_name, unquote_name(right[0].split('.')[1]),
                               None, 'in', None, ids)
                    lookups.append(l.as_sql())
            lookup_str = ' AND '.join(lookups)
            table = server[unquote_name(leftmost_table_name)]
            if len(self.params[1])==1 and self.params[1][0]=='COUNT(*)':
                joined_view = self.simple_select(server, table,
                                                 (leftmost_table_name+'.'+'"id"',),
                                                 lookup_str, params)
                cursor.save_one(len(joined_view))
            else:
                joined_view = self.simple_select(server, table,
                                                 self.params[1],
                                                 lookup_str, params)
                cursor.save_view(joined_view)

    def execute_delete(self, server, params):
        # self.params ---(table_name, where)
        table_name = self.params[0]
        if is_fake(table_name):
            print "%s is fake, skipping delete" % table_name
            return
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
        elif self.command == 'update':
            return self.execute_update(server, params)
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
        #~ raise NotImplementedError
        pass

class CursorWrapper(object):
    """
    @summary: DB-API 2.0 Cursor object for Django CouchDB backend.
    """
    def __init__(self, server, username=None, password=None):
        assert isinstance(server, couchdb.Server), \
            'Please, supply ``couchdb.Server`` instance as first argument.'

        self.server = server
        self._username, self._password = username, password
        self.saved_view = None
        self.saved_one = None

    def execute(self, sql, params=()):
        if isinstance(sql, SQL):
            sql.execute_sql(self, params)

    def save_view(self, view): # fetch here?
        self.saved_view = view
        self.saved_view_offset = 0

    @property
    def rowcount(self):
        if self.saved_view:
            return len(self.saved_view)
        else:
            return 0

    def save_one(self, one):
        self.saved_one = one

    def fetchone(self):
        return [self.saved_one]

    def fetchmany(self, count):
        ret = list(self.saved_view)[self.saved_view_offset:self.saved_view_offset+count]
        self.saved_view_offset += count
        if type(self.saved_view) is list:
            return ret
        else:
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
            #~ print "SQL:", unicode(sql)
            #~ print "PARAMS:", params
            super(DebugCursorWrapper, self).execute(sql, params)
        finally:
            stop = time()
            #~ sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            #~ self.db.queries.append({
                #~ 'sql': sql,
                #~ 'time': "%.3f" % (stop - start),
            #~ })



