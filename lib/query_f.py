from .. import config
from sqlalchemy.orm import aliased
from . import converters, consts

class CQuery(object):
    """An object for storing the query being built."""
    
    def __init__(self, data):
        super(CQuery, self).__init__()
        self.data = data
        
        self.aliases = {}
        
        self.columns   = []
        self.filters   = []
        self.order_bys = []
        self.group_bys = []
    
    def check_for_aliases(self, data):
        """
        Goes through all referenced fields and checks to see if they
        are in the alias list. Any it finds it adds aliases for and
        extends the filters so the alias will be linked to.
        """
        total_columns = data['columns'] + [data['key']] + [f['column'] for f in data['filters']]
        
        for table_column in filter(None, total_columns):
            t, c = table_column.split(".")
            table = config['sources'][t]
            
            if c in table.aliases:
                the_alias = table.aliases[c]
                
                # We don't want to make the same alias twice
                if the_alias['name'] in self.aliases:
                    continue
                
                # Create the alias
                alias_class = the_alias['db_class']
                alias_instance = aliased(alias_class, name=the_alias['name'])
                self.aliases[the_alias['name']] = alias_instance
                
                # Link the alias with a filter
                local_column = config['metadata'].tables[t].columns[c]
                alias_column = getattr(alias_instance, the_alias['join_on'])
                
                self.filters.append(local_column == alias_column)
    
    def get(self, identifier, use_alias=True, pure=False):
        """
        Used to grab a column but possibly to wrap it in an aggregate
        """
        c = self.get_column(identifier, use_alias=use_alias)
        
        if not self.data['group_by'] or pure:
            return c
        
        f = self.data['group_by_funcs'].get(identifier, "-")
        
        if f == "-":
            return c
        
        return consts.group_lookup[f](c)
    
    def get_column(self, identifier, use_alias=True):
        """
        Grabs a column or an alias of a column if it's meant to be using one.
        """
        table, column = identifier.split('.')
        table_source = config['sources'][table]
        
        # First check if it's an alias
        if column in table_source.aliases:
            the_alias = table_source.aliases[column]
            
            if use_alias:
                alias_table = self.aliases[the_alias['name']]
                return getattr(alias_table, the_alias['column'])
            
            # We're not using the table alias because the
            # version of SQLAlchemy for zope doesn't have what we need
            # instead we're going to get the actual target of the alias
            # rather than the aliased target
            target_table = the_alias['table']
            target_column = the_alias['column']
            
            return config['metadata'].tables[target_table].columns[target_column]
         
        # If not then grab the column itself
        return config['metadata'].tables[table].columns[column]

def build(data):
    q = CQuery(check_query_data(data))
    q.check_for_aliases(data)
    
    # columns
    if data['key'] != None:
        q.columns.append(q.get(data['key']))
    
    for c in data['columns']:
        q.columns.append(q.get(c))
    
    # Filters
    for f in data['filters']:
        filter_col = q.get(f['column'], pure=True)
        op_func = getattr(filter_col, consts.operator_lookup[f['operator']])
        
        t, c = f['column'].split(".")
        source_table = config['sources'][t]
        # config['sources'][table]
        # if column in table_source.aliases:
        
        # Convert it from a string into the relevant database type
        value = converters.typecast(q.get(f['column'], use_alias=False, pure=True), f['value'])
        
        # Apply conversion functions to it
        value = converters.convert(value, source_table.column_converters.get(c, []))
        
        q.filters.append(op_func(value))
    
    # TODO desc/asc
    if data['key'] != None:
        q.order_bys.append(q.get(data['key']))
    
    # Grouping by
    potential_groupings = list(data['columns'])
    if data['key'] != None:
        potential_groupings.append(data['key'])
    
    prelude = lambda i: data['group_by_funcs'].get(i, "-") == "-"
    for pg in filter(prelude, potential_groupings):
        q.group_bys.append(q.get(pg, pure=True))
    
    if len(q.columns) == 0:
        return [], q
    
    # For debug
    print("\n\n")
    print(q.columns)
    print(q.filters)
    print(q.order_bys)
    print(q.group_bys)
    print("\n\n")
    
    return config['DBSession'].query(*q.columns).filter(*q.filters).order_by(*q.order_bys).group_by(*q.group_bys).limit(400), q

def check_query_data(data):
    data['key']            = data.get('key', None)
    data['columns']        = data.get('columns', [])
    data['filters']        = data.get('filters', [])
    data['group_by']       = data.get('group_by', False)
    data['group_by_funcs'] = data.get('group_by_funcs', {})
    return data
