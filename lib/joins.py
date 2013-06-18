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

def filter_dict(prelude, the_dict, by_key=True):
    """Takes a dictionary and filters it. I couldn't find
    an equivilent to filter for dictionaries in the standard lib"""
    
    if by_key:
        for k, v in the_dict.items():
            if prelude(k):
                yield k, v
    else:
        for k, v in the_dict.items():
            if prelude(v):
                yield k, v

def remove_join(data, join_id):
    """When we remove the join we need to remove the reference to that table
    everywhere else. Otherwise it'll be interesting."""
    
    join_to_remove = data['joins'][join_id]
    source_to_remove = join_to_remove['right'].split(".")[0]
    
    def not_source(v):
        if v is None: return True
        if v == source_to_remove: return False
        if v.split(".")[0] == source_to_remove: return False
        return True
    
    data['sources'] = list(filter(not_source, data['sources']))
    data['columns'] = list(filter(not_source, data['columns']))
    data['group_by_funcs'] = dict(filter_dict(not_source, data['group_by_funcs']))
    
    new_filters = []
    for f in data['filters']:
        if not_source(f['column']):
            new_filters.append(f)
    data['filters'] = new_filters
    
    if not not_source(data['key']):
        data['key'] = None
    
    # Finally, remove the join itself
    data['joins'] = data['joins'][:join_id] + data['joins'][join_id+1:]
    
    return data
