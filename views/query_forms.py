# import transaction
# import datetime

from pyramid.httpexceptions import HTTPFound

# from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

# import json
# from ..lib import html_f, consts
from .. import config

def edit_columns(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    columns = []
    for s, the_source in config['sources'].items():
        for c in the_source.columns:
            key = "{}.{}".format(s, c)
            if key in request.params:
                columns.append(key)
    
    the_query.jdata['columns'] = columns
    the_query.compress_data()
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#columns" % request.route_url("concision.query.edit", query_id=query_id))

def add_filter(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_filter = {
        "column": request.params['column'],
        "operator": request.params['operator'],
        "value": request.params['value'],
    }
    
    existing_filters = the_query.jdata.get('filters', [])
    existing_filters.append(new_filter)
    the_query.jdata['filters'] = existing_filters
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#filters" % request.route_url("concision.query.edit", query_id=query_id))

def edit_filter(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_filter = {
        "column": request.params['column'],
        "operator": request.params['operator'],
        "value": request.params['value'],
    }
    filter_id = int(request.params['filter_id'])
    
    existing_filters = the_query.jdata.get('filters', [])
    existing_filters[filter_id] = new_filter
    the_query.jdata['filters'] = existing_filters
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#filters" % request.route_url("concision.query.edit", query_id=query_id))

def delete_filter(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    filter_id = int(request.params['f'])
    existing_filters = the_query.jdata.get('filters', [])
    
    try:
        existing_filters = existing_filters[:filter_id] + existing_filters[filter_id+1:]
    except Exception:
        raise
    
    the_query.jdata['filters'] = existing_filters
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#filters" % request.route_url("concision.query.edit", query_id=query_id))

def edit_key(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    the_query.jdata['key'] = request.params.get('query_key', None)
    the_query.compress_data()
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#graphing" % request.route_url("concision.query.edit", query_id=query_id))

def edit_groupby(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    the_query.jdata['group_by'] = "group_by" in request.params
    
    groupings = {}
    for s, the_source in config['sources'].items():
        for c in the_source.columns:
            key = "{}.{}".format(s, c)
            if key in request.params:
                groupings[key] = request.params[key]
    
    the_query.jdata['group_by_funcs'] = groupings
    the_query.compress_data()
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#groupby" % request.route_url("concision.query.edit", query_id=query_id))
    
def add_orderby(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_orderby = {
        "column": request.params['column'],
        "order": request.params['order'],
    }
    
    existing_orderby = the_query.jdata.get('orderby', [])
    existing_orderby.append(new_orderby)
    the_query.jdata['orderby'] = existing_orderby
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#orderby" % request.route_url("concision.query.edit", query_id=query_id))

def edit_orderby(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_orderby = {
        "column": request.params['column'],
        "order": request.params['order'],
    }
    orderby_id = int(request.params['orderby_id'])
    
    existing_orderby = the_query.jdata.get('orderby', [])
    existing_orderby[orderby_id] = new_orderby
    the_query.jdata['orderby'] = existing_orderby
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#orderby" % request.route_url("concision.query.edit", query_id=query_id))

def delete_orderby(request):
    request.do_not_log = True
    config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    orderby_id = int(request.params['o'])
    existing_orderby = the_query.jdata.get('orderby', [])
    
    try:
        existing_orderby = existing_orderby[:orderby_id] + existing_orderby[orderby_id+1:]
    except Exception:
        raise
    
    the_query.jdata['orderby'] = existing_orderby
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#orderby" % request.route_url("concision.query.edit", query_id=query_id))
