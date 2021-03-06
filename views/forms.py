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
    existing_groupbys = the_query.jdata.get('groupby', [])
    
    if action == "add":
        new_column = " ".join(filter(None, (
            request.params['function0'],
            request.params['function1'],
            request.params['function2'],
            request.params['column'],
        )))
        
        existing_columns.append(new_column)
        existing_groupbys.append("-")
        
    elif action == "delete":
        column_id = int(request.params['column'])
        
        existing_columns = existing_columns[:column_id] + existing_columns[column_id+1:]
        existing_groupbys = existing_groupbys[:column_id] + existing_groupbys[column_id+1:]
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['columns'] = existing_columns
    the_query.jdata['groupby'] = existing_groupbys
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#columns" % request.route_url("concision.query.overview", query_id=query_id))

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
    
    return HTTPFound(location="%s#filters" % request.route_url("concision.query.overview", query_id=query_id))

def orderby(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    action = request.params['action']
    existing_orderbys = the_query.jdata.get('orderby', [])
    
    if action == "add":
        new_orderby = {
            "order": request.params['order'],
            "column": " ".join(filter(None, (
                request.params['function0'],
                request.params['function1'],
                request.params['function2'],
                request.params['column'],
            )))
        }
        
        existing_orderbys.append(new_orderby)
        
    elif action == "delete":
        order_id = int(request.params['order'])
        
        existing_orderbys = existing_orderbys[:order_id] + existing_orderbys[order_id+1:]
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['orderby'] = existing_orderbys
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#orderby" % request.route_url("concision.query.overview", query_id=query_id))

def groupby(request):
    request.do_not_log = True
    action = request.params.get('action', 'add')
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    if action == "add":
        groupbys = []
        
        if 'key' in request.params:
            the_query.jdata['groupby_key'] = request.params['key']
        
        for i, c in enumerate(data['columns']):
            groupbys.append(request.params[str(i)])
            
    elif action == "delete":
        groupbys = []
        
        if 'key' in request.params:
            the_query.jdata['groupby_key'] = "-"
        
        for i, c in enumerate(data['columns']):
            groupbys.append("-")
    
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['groupby'] = groupbys
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#groupby" % request.route_url("concision.query.overview", query_id=query_id))

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
        if 'groupby_key' in the_query.jdata:
            del(the_query.jdata['groupby_key'])
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    the_query.jdata['key'] = new_key
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#graphing" % request.route_url("concision.query.overview", query_id=query_id))

def other(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    action = request.params['action']
    
    if action == "edit":
        the_query.name = request.params['query_name'].strip()
        
    else:
        raise KeyError("No handler for action of '%s'" % action)
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#other" % request.route_url("concision.query.overview", query_id=query_id))