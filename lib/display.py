"""
Functions used to display information about the query.
"""
from .. import config
from . import converters

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
    for i, description in enumerate(data['columns']):
        funcs, table, column = converters.get_parts(description)
        
        source = config['sources'][table]
        r = {
            "id": i,
            "name": "%s %s" % (" ".join(funcs), source.column_labels[column]),
            "table": source.label,
        }
        
        yield r



