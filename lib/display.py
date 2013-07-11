"""
Functions used to display information about the query.
"""
from .. import config
from . import converters, consts, filter_funcs

"""
    # Columns
    relevant_sources = [s for s in config['sources'].items() if s[0] in data['sources']]
    existing_columns = data.get('columns', [])
    
    # Filters
    columns = []
    for s in data['sources']:
        the_source = config['sources'][s]
        columns.extend([("%s.%s" % (s, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    # Group by
    selected_columns = defaultdict(list)
    for s in data['sources']:
        prelude = lambda c: '%s.%s' % (s, c) in data.get('columns', []) or '%s.%s' % (s, c) == data.get('key', "")
        
        the_source = config['sources'][s]
        selected_columns[s] = list(filter(prelude, the_source.columns))
    
    # Joins
    current_source_joins = joins.current_source_joins(data)
    possible_source_joins = joins.possible_source_joins(data)
    """

def tablist(data):
    tablist = set(["tables"])
    
    if len(data.get('tables', [])) > 0:
        tablist.add('columns')
        tablist.add('filters')
    
    if len(data.get('columns', [])) > 0:
        tablist.add('execute')
        tablist.add('groupby')
        tablist.add('orderby')
        tablist.add('graphing')
    
    if data.get('key', None) is not None:
        tablist.add('view_graph')
    
    return tablist

def tables(data):
    for i, t in enumerate(data.get('tables', [])):
        source = config['sources'][t]
        r = {
            "id": i,
            "name": source.label,
        }
        
        yield r

def columns(data):
    for i, the_column in enumerate(data['columns']):
        funcs, table, column = converters.get_parts(the_column)
        
        func_labels = map(
            lambda k: consts.all_funcs[k],
            funcs,
        )
        
        source = config['sources'][table]
        r = {
            "id": i,
            "name": "%s %s" % (" ".join(func_labels), source.column_labels[column]),
            "table": source.label,
        }
        
        yield r

# def filters(data):
#     for i, the_filter in enumerate(data['filters']):
#         funcs, table, filter = converters.get_parts(the_filter['column'])
        
#         func_labels = map(
#             lambda k: consts.all_funcs[k],
#             funcs,
#         )
        
#         source = config['sources'][table]
#         r = {
#             "id": i,
#             "name": "%s %s" % (" ".join(func_labels), source.column_labels[filter]),
#             "table": source.label,
#             "operator": consts.operators[the_filter['operator']],
#             "value": the_filter['value'],
#         }
        
#         yield r

def query_key(data):
    if data['key'] == None:
        return None
    
    funcs, table, column = converters.get_parts(data['key'])
        
    func_labels = map(
        lambda k: consts.all_funcs[k],
        funcs,
    )
    
    source = config['sources'][table]
    r = {
        "name": "%s %s" % (" ".join(func_labels), source.column_labels[column]),
        "table": source.label,
    }
    
    return r

def filter_html(data):
    return "".join(filter_funcs._filter_group(data))
