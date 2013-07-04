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

def adv_do_column(request):
    request.do_not_log = True
    # the_user  = config['get_user_func'](request)
    
    query_id  = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    the_query.extract_data()
    
    new_column = {
        "column": request.params['column'],
        "functions": [request.params['function0'], request.params['function1'], request.params['function2']],
    }
    
    existing_columns = the_query.jdata.get('columns', [])
    existing_columns.append(new_column)
    the_query.jdata['columns'] = existing_columns
    the_query.compress_data()
    
    config['DBSession'].add(the_query)
    
    return HTTPFound(location="%s#columns" % request.route_url("concision.adv_query.columns", query_id=query_id))

# def adv_edit_column(request):
#     request.do_not_log = True
#     # the_user  = config['get_user_func'](request)
    
#     query_id  = int(request.matchdict['query_id'])
#     the_query = config['DBSession'].query(StoredQuery).column(StoredQuery.id == query_id).first()
#     the_query.extract_data()
    
#     new_column = {
#         "column": request.params['column'],
#         "operator": request.params['operator'],
#         "value": request.params['value'],
#     }
#     column_id = int(request.params['column_id'])
    
#     existing_columns = the_query.jdata.get('columns', [])
#     existing_columns[column_id] = new_column
#     the_query.jdata['columns'] = existing_columns
#     the_query.compress_data()
    
#     config['DBSession'].add(the_query)
    
#     return HTTPFound(location="%s#columns" % request.route_url("concision.query.edit", query_id=query_id))

# def adv_delete_column(request):
#     request.do_not_log = True
#     # the_user  = config['get_user_func'](request)
    
#     query_id  = int(request.matchdict['query_id'])
#     the_query = config['DBSession'].query(StoredQuery).column(StoredQuery.id == query_id).first()
#     the_query.extract_data()
    
#     column_id = int(request.params['f'])
#     existing_columns = the_query.jdata.get('columns', [])
    
#     existing_columns = existing_columns[:column_id] + existing_columns[column_id+1:]
    
#     the_query.jdata['columns'] = existing_columns
#     the_query.compress_data()
    
#     config['DBSession'].add(the_query)
    
#     return HTTPFound(location="%s#columns" % request.route_url("concision.query.edit", query_id=query_id))