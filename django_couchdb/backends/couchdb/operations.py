from django.db.backends import BaseDatabaseOperations
from utils import *
from queries import *
from nodes import *

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
        s = Sequence(cursor.server, table_name)
        return s.currval()

    def query_class(self, DefaultQueryClass):
        class CustomQuery(DefaultQueryClass):
            def clone(self, klass=None, **kwargs):
                if klass:
                    if klass.__name__ == 'InsertQuery':
                        klass = get_insert_query(klass)
                    elif klass.__name__ == 'UpdateQuery':
                        klass = get_update_query(klass) # update == insert
                    elif klass.__name__ == 'DeleteQuery':
                        klass = get_delete_query(klass)
                return super(CustomQuery, self).clone(klass, **kwargs)
            def __new__(cls, *args, **kwargs):
                if cls.__name__ == 'InsertQuery':
                    NewInsertQuery = get_insert_query(cls)
                    obj =  super(CustomQuery, NewInsertQuery).__new__(NewInsertQuery, *args, **kwargs)
                elif cls.__name__ == 'UpdateQuery':
                    NewUpdateQuery = get_update_query(cls) # update == insert
                    obj =  super(CustomQuery, NewUpdateQuery).__new__(NewUpdateQuery, *args, **kwargs)
                elif cls.__name__ == 'DeleteQuery':
                    NewDeleteQuery = get_delete_query(cls)
                    obj =  super(CustomQuery, NewDeleteQuery).__new__(NewDeleteQuery, *args, **kwargs)
                else:
                    obj =  super(CustomQuery, cls).__new__(cls, *args, **kwargs)
                return obj
            def __init__(self, model, connection, where=None):
                from django.db.models.sql.where import WhereNode
                where = where or WhereNode
                NewWhereNode = get_where_node(where)
                super(CustomQuery, self).__init__(model, connection, where=NewWhereNode)
            def as_sql(self, with_limits=True, with_col_aliases=False):
                """
                Creates the SQL for this query. Returns the SQL string and list of
                parameters.

                If 'with_limits' is False, any limit/offset information is not included
                in the query.
                """
                self.pre_sql_setup()
                out_cols = self.get_columns(with_col_aliases)
                ordering = self.get_ordering()

                # This must come after 'select' and 'ordering' -- see docstring of
                # get_from_clause() for details.
                from_, f_params = self.get_from_clause()

                where, w_params = self.where.as_sql(qn=self.quote_name_unless_alias)
                params = []
                for val in self.extra_select.itervalues():
                    params.extend(val[1])

                SQL_params = []
                #~ result = ['SELECT']
                if self.distinct:
                    #~ result.append('DISTINCT')
                    SQL_params.append(True)
                else:
                    SQL_params.append(False)

                SQL_params.append(out_cols + self.ordering_aliases)
                SQL_params.append(from_)

                params.extend(f_params)

                if where:
                    SQL_params.append(where)
                    params.extend(w_params)
                else:
                    SQL_params.append(None)
                if self.extra_where:
                    SQL_params.append(self.extra_where)
                else:
                    SQL_params.append(None)

                if self.group_by:
                    grouping = self.get_grouping()
                    SQL_params.append(grouping)
                else:
                    SQL_params.append(None)

                if self.having:
                    having, h_params = self.get_having()
                    SQL_params.append(having)
                    params.extend(h_params)
                else:
                    SQL_params.append(None)

                if ordering:
                    SQL_params.append(ordering)
                else:
                    SQL_params.append(None)

                if with_limits:
                    SQL_params.append((self.low_mark, self.high_mark))
                else:
                    SQL_params.append(None)

                params.extend(self.extra_params)
                return SQL('select', SQL_params), tuple(params)

        return CustomQuery

