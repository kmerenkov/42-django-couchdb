from utils import *

def get_insert_query(BaseQuery):
    class InsertQuery(BaseQuery):
        def as_sql(self):
            return SQL('insert',(self.model._meta.db_table, self.columns, self.values)), self.params
    return InsertQuery


def get_delete_query(BaseQuery):
    class DeleteQuery(BaseQuery):
        def as_sql(self):
            assert len(self.tables) == 1, \
                    "Can only delete from one table at a time."
            where, params = self.where.as_sql()
            return SQL('delete',(self.quote_name_unless_alias(self.tables[0]), where)), tuple(params)
    return DeleteQuery
