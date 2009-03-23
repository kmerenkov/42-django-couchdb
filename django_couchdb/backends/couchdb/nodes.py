def process_name(name):
    if name =='id':
        return '_id'
    else:
        return name

def operator_lookup(name, operator, params):
    return "d."+process_name(name) + " %s " % (operator,) + "\"%s\"" % tuple(params)

class Lookup(object):
    operators = {
        'exact': '==',
        #~ 'iexact': '= UPPER(%s)',
        #~ 'contains': 'LIKE %s',
        #~ 'icontains': 'LIKE UPPER(%s)',
        #~ 'regex': '~ %s',
        #~ 'iregex': '~* %s',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
        #~ 'startswith': 'LIKE %s',
        #~ 'endswith': 'LIKE %s',
        #~ 'istartswith': 'LIKE UPPER(%s)',
        #~ 'iendswith': 'LIKE UPPER(%s)',
    }

    def __init__(self, table_alias, name, db_type, lookup_type, value_annot, params):
        self.table_alias = table_alias
        self.name = name
        self.db_type = db_type
        self.lookup_type = lookup_type
        self.value_annot = value_annot
        self.params = params

        self.as_sql = getattr(self,'lookup_'+lookup_type, None)
        if self.as_sql is None:
            if lookup_type in self.operators:
                self.as_sql = lambda : operator_lookup(self.name,
                                                        self.operators[lookup_type],
                                                        self.params)
            else:
                self.as_sql = self.dummy_lookup

    def dummy_lookup(self, *args):
        raise TypeError('Invalid lookup_type: %r' % self.lookup_type)


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

