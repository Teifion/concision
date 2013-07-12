# import transaction
# import datetime

from pyramid.httpexceptions import HTTPFound

# from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

# import json
from ..lib import query_f, filter_funcs
from .. import config

def table(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    action = request.params['action']
    existing_tables = the_query.jdata.get('tables', [])
    
    if action == "add":
        if data['tables'] == []:
            existing_tables = [request.params['table']]
        
        else:
            raise Exception("Can't have more than 1 table yet")
            # existing_tables.append(new_table)
    
    elif action == "delete":
        table_id = int(request.params['table'])
        table_name = existing_tables[table_id]
        
        membership_tester = lambda v: ("%s." % table_name) not in v
        data['columns'] = list(filter(membership_tester, data['columns']))
        
        membership_tester = lambda v: ("%s." % table_name) not in v['column']
        data['filters'] = list(filter(membership_tester, data['filters']))
        
        if ("%s." % table_name) in data['key']:
            data['key'] = None
        
        existing_tables = existing_tables[:table_id] + existing_tables[table_id+1:]
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
        
    the_query.jdata['tables'] = existing_tables
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#tables" % request.route_url("concision.query.overview", query_id=query_id))

def column(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    action = request.params['action']
    existing_columns = the_query.jdata.get('columns', [])
    
    if action == "add":
        new_column = " ".join(filter(None, (
            request.params['function0'],
            request.params['function1'],
            request.params['function2'],
            request.params['column'],
        )))
        
        existing_columns.append(new_column)
        
    elif action == "delete":
        column_id = int(request.params['column'])
        existing_columns = existing_columns[:column_id] + existing_columns[column_id+1:]
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['columns'] = existing_columns
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#columns" % request.route_url("concision.query.columns", query_id=query_id))

def filters(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    action = request.params['action']
    existing_filters = the_query.jdata.get('filters', [])
    
    if action == "add_item":
        column = " ".join(filter(None, (
            request.params['function0'],
            request.params['function1'],
            request.params['function2'],
            request.params['column'],
        )))
        
        max_id = filter_funcs.get_max_id(existing_filters) + 1
        new_item = {
            "column": column,
            "operator": request.params['operator'],
            "value": request.params['value'].strip(),
            "id": max_id,
        }
        
        existing_filters = filter_funcs.add_item(existing_filters, int(request.params['item_id']), new_item)
    
    elif action == "add_group":
        max_id = filter_funcs.get_max_id(existing_filters) + 1
        new_item = {
            "type": request.params['type'],
            "contents": [],
            "id": max_id,
        }
        
        existing_filters = filter_funcs.add_item(existing_filters, int(request.params['item_id']), new_item)
    
    elif action == "delete":
        filter_id = int(request.params['filter'])
        existing_filters = filter_funcs.delete_filter(existing_filters, filter_id)
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['filters'] = existing_filters
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#filters" % request.route_url("concision.query.filters", query_id=query_id))

def do_key(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    action = request.params['action']
    
    if action == "add":
        new_key = " ".join(filter(None, (
            request.params['function0'],
            request.params['function1'],
            request.params['function2'],
            request.params['key'],
        )))
        
        if new_key == "":
            new_key = None
        
    elif action == "delete":
        new_key = None
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['key'] = new_key
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#graphing" % request.route_url("concision.query.graphing", query_id=query_id))