from .. import config
from collections import OrderedDict

def current_source_joins(data):
    results = OrderedDict()
    
    for s in data['sources']:
        the_source = config['sources'][s]
        
        for c in the_source.allow_join:
            results["%s.%s" % (s, c)] = "%s: %s" % (the_source.label, the_source.column_labels[c])
    
    return results

def possible_source_joins(data):
    results = OrderedDict()
    
    for s, the_source in config['sources'].items():
        if s in data['sources']: continue
        
        for c in the_source.allow_join:
            results["%s.%s" % (s, c)] = "%s: %s" % (the_source.label, the_source.column_labels[c])
    
    return results

def remove_join(data, join_id):
    join_to_remove = existing_joins[join_id]
    source_to_remove = join_to_remove.split("")
    
    existing_joins = existing_joins[:join_id] + existing_joins[join_id+1:]
    
    the_query.jdata['join'] = existing_joins
    the_query.compress_data()
    
    return data
