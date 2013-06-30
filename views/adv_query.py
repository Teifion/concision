# from pyramid.httpexceptions import HTTPFound
# from pyramid.response import Response

from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

from ..lib import (
    html_f,
    consts,
    query_f,
    graphing,
    pretty_sql,
    joins,
    display,
)
from .. import config

def adv_overview(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        columns   = display.columns(data),
        query_id  = query_id,
        # sources   = config['sources'],
        # selected_columns = selected_columns,
        # relevant_sources = relevant_sources,
        
        # current_source_joins = current_source_joins,
        # possible_source_joins = possible_source_joins,
        
        # html_f = html_f,
        # consts = consts,
    )

def adv_columns(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        columns   = display.columns(data),
        query_id  = query_id,
    )
