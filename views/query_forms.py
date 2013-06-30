# import transaction
# import datetime

from pyramid.httpexceptions import HTTPFound

# from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

# import json
from ..lib import joins
from .. import config

def alter_query_type(request):
    request.do_not_log = True
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_type = request.params['new_type']
    the_query.jdata['type'] = new_type
    the_query.compress_data()
    config['DBSession'].add(the_query)
    
    if new_type == "advanced":
        return HTTPFound(location=request.route_url("concision.adv_query.overview", query_id=query_id))
    return HTTPFound(location="%s#columns" % request.route_url("concision.query.edit", query_id=query_id))

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
    
    existing_filters = existing_filters[:filter_id] + existing_filters[filter_id+1:]
    
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
    # config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    orderby_id = int(request.params['o'])
    existing_orderby = the_query.jdata.get('orderby', [])
    
    existing_orderby = existing_orderby[:orderby_id] + existing_orderby[orderby_id+1:]
    
    the_query.jdata['orderby'] = existing_orderby
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#orderby" % request.route_url("concision.query.edit", query_id=query_id))

def add_join(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_join = {
        "left": request.params['left'],
        "right": request.params['right'],
    }
    
    new_source = request.params['right'].split(".")[0]
    
    existing_joins = the_query.jdata.get('joins', [])
    existing_joins.append(new_join)
    the_query.jdata['joins'] = existing_joins
    the_query.jdata['sources'].append(new_source)
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#join" % request.route_url("concision.query.edit", query_id=query_id))

def delete_join(request):
    request.do_not_log = True
    # config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    join_id = int(request.params['j'])
    the_query.jdata = joins.remove_join(the_query.jdata, join_id)
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#join" % request.route_url("concision.query.edit", query_id=query_id))
