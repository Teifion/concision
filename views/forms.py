# import transaction
# import datetime

from pyramid.httpexceptions import HTTPFound

# from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

# import json
from ..lib import query_f
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
    
    if action == "add":
        column = " ".join(filter(None, (
            request.params['function0'],
            request.params['function1'],
            request.params['function2'],
            request.params['filter'],
        )))
        
        new_filter = {
            "column": column,
            "operator": request.params['operator'],
            "value": request.params['value'].strip(),
        }
        
        existing_filters.append(new_filter)
        
    elif action == "delete":
        filter_id = int(request.params['filter'])
        existing_filters = existing_filters[:filter_id] + existing_filters[filter_id+1:]
        
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
    
    new_key = " ".join(filter(None, (
        # request.params['function0'],
        # request.params['function1'],
        # request.params['function2'],
        request.params['key'],
    )))
    
    if new_key == "":
        new_key = None
    
    the_query.jdata['key'] = new_key
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#graphing" % request.route_url("concision.query.graphing", query_id=query_id))