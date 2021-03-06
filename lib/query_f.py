from .. import config
from sqlalchemy.orm import aliased
from . import converters, consts, filter_funcs

class CQuery(object):
    """An object for storing the query being built."""
    
    def __init__(self, data):
        super(CQuery, self).__init__()
        self.data = data
        
        self.aliases = {}
        
        self.columns     = []
        self.filters     = []
        self.order_bys   = []
        self.group_bys   = []
        self.joins       = []
        self.alias_joins = []
    
    def check_for_aliases(self, data):
        """
        Goes through all referenced fields and checks to see if they
        are in the alias list. Any it finds it adds aliases for and
        extends the filters so the alias will be linked to.
        """
        total_columns = data['columns'] + [data['key']] + filter_funcs.get_columns(data['filters'])
        total_columns.extend([o['column'] for o in data['orderby']])
        
        for table_column in filter(None, total_columns):
            f, t, c = converters.get_parts(table_column)
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
                
                self.alias_joins.append(local_column == alias_column)
    
    def get_raw(self, identifier):
        """Gets the column, ignoring anything about aliases etc"""
        func, table, column = converters.get_parts(identifier)
        table_source = config['sources'][table]
        return config['metadata'].tables[table].columns[column]
    
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
        funcs, table, column = converters.get_parts(identifier)
        table_source = config['sources'][table]
        
        # First check if it's an alias
        if column in table_source.aliases:
            the_alias = table_source.aliases[column]
            
            if use_alias:
                alias_table = self.aliases[the_alias['name']]
                the_value = getattr(alias_table, the_alias['column'])
                return converters.apply_functions(the_value, funcs)
            
            # We're not using the table alias because the
            # version of SQLAlchemy for zope doesn't have what we need
            # instead we're going to get the actual target of the alias
            # rather than the aliased target
            target_table = the_alias['table']
            target_column = the_alias['column']
            
            the_value = config['metadata'].tables[target_table].columns[target_column]
            return converters.apply_functions(the_value, funcs)
            # return config['metadata'].tables[target_table].columns[target_column]
         
        # If not then grab the column itself
        the_value = config['metadata'].tables[table].columns[column]
        return converters.apply_functions(the_value, funcs)
        # return config['metadata'].tables[table].columns[column]

def build(data):
    q = CQuery(check_query_data(data))
    q.check_for_aliases(data)
    
    # columns
    for c in data['columns']:
        q.columns.append(q.get(c))
    
    if data['key'] != None:
        q.columns.append(q.get(data['key']))
    
    # Filters
    """
    for f in data['filters']:
        filter_col = q.get(f['column'], pure=True)
        op_func = getattr(filter_col, consts.operator_lookup[f['operator']])
        
        funcs, t, c = converters.get_parts(f['column'])
        source_table = config['sources'][t]
        # config['sources'][table]
        # if column in table_source.aliases:
        
        value = f['value']
        
        # Enum?
        if c in source_table.enums:
            if value in source_table.enums[c]:
                value = source_table.enums[c].index(value)
            else:
                continue
        
        # Convert it from a string into the relevant database type
        value = converters.typecast(q.get(f['column'], use_alias=False, pure=True), value)
        
        # Apply conversion functions to it
        value = converters.convert(value, source_table.column_converters.get(c, []))
        
        # Apply filter type converts to it
        value = consts.operator_converters[f['operator']](value)
        
        q.filters.append(op_func(value))
    """
    
    q.filters = [filter_funcs.build(q, data['filters'])]
    
    for aj in q.alias_joins:
        q.filters.append(aj)
    
    # Mandatory filters
    for t in data['tables']:
        the_source = config['sources'][t]
        q.filters.extend(the_source.mandatory_filters())
    
    # Order bys
    if data['key'] != None:
        q.order_bys.append(q.get(data['key']))
    
    for o in data['orderby']:
        order_col = q.get(o['column'], pure=True)
        
        if o['order'] == "DESC":
            order_func = order_col.desc()
        elif o['order'] == "ASC":
            order_func = order_col.asc()
        else:
            raise KeyError("No ordering of '%s'" % o['order'])
        
        q.order_bys.append(order_func)
    
    # Grouping by
    if any(map(lambda g: g != "-", data['groupby'] + [data.get('groupby_key', "-")])):
        new_columns = []
        
        for i, c in enumerate(q.columns):
            if i == len(q.columns)-1 and data['key'] != None:
                grp = data['groupby_key']
            else:
                grp = data['groupby'][i]
                
            if grp == "-":
                new_columns.append(c)
                q.group_bys.append(c)
                
            else:
                new_columns.append(consts.function_lookup[grp](c))
        
        q.columns = new_columns
    
    if len(q.columns) == 0:
        return [], q
        # q.columns.append("COUNT(*)")
    
    the_query = config['DBSession'].query(*q.columns)
    
    for j in data['joins']:
        left = q.get_raw(j['left'])
        right = q.get_raw(j['right'])
        
        target_table = config['sources'][j['right'].split(".")[0]].db_class
        
        the_join = (target_table, (left == right))
        q.joins.append(the_join)
    
    # For debug
    # print("\n\n")
    # print(q.columns)
    # print(q.filters)
    # print(q.order_bys)
    # print(q.group_bys)
    # print(q.joins)
    # print(q.alias_joins)
    # print("\n\n")
    
    # Add all calculated joins and all filter/alias related ones too
    for j in q.joins:
        the_query = the_query.join(*j)
    
    the_query = the_query.filter(*q.filters).order_by(*q.order_bys).group_by(*q.group_bys).limit(400)
    
    return the_query, q

def check_query_data(data):
    data['key']            = data.get('key', None)
    data['tables']         = data.get('tables', [])
    data['columns']        = data.get('columns', [])
    data['filters']        = data.get('filters', {"type":"and","id":1,"contents":[]})
    data['group_by']       = data.get('group_by', False)
    data['group_by_funcs'] = data.get('group_by_funcs', {})
    data['orderby']        = data.get('orderby', [])
    data['joins']          = data.get('joins', [])
    return data
