from utils import *

def get_insert_query(BaseQuery):
    class InsertQuery(BaseQuery):
        def as_sql(self):
            return SQL('insert',(self.model._meta.db_table, self.columns, self.values)), self.params
    return InsertQuery
