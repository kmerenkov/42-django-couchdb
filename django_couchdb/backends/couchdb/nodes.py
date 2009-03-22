def process_name(name):
    if name =='id':
        return '_id'
    else:
        return name

class Lookup(object):
    def __init__(self, table_alias, name, db_type, lookup_type, value_annot, params):
        self.table_alias = table_alias
        self.name = name
        self.db_type = db_type
        self.lookup_type = lookup_type
        self.value_annot = value_annot
        self.params = params

        self.as_sql = getattr(self,'lookup_'+lookup_type)
        if self.as_sql is None:
            self.as_sql = self.dummy_lookup

    def dummy_lookup(self, *args):
        raise TypeError('Invalid lookup_type: %r' % self.lookup_type)

    def lookup_exact(self):
        return "d."+process_name(self.name) + " == " + "\"%s\"" % tuple(self.params)

    def lookup_in(self):
        params = '{'+','.join('%s: 1' % x for x in self.params) + '}'
        return "d." + process_name(self.name) + " in %s" % params


def get_where_node(BaseNode):
    class WhereNode(BaseNode):
        def make_atom(self, child, qn):
            #~ table_alias, name, db_type, lookup_type, value_annot, params = child
            lookup = Lookup(*child)
            return lookup.as_sql(), []
    return WhereNode

