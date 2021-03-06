from pyramid.httpexceptions import HTTPFound
# from pyramid.response import Response
from collections import defaultdict

from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

import json

from ..lib import (
    html_f,
    consts,
    query_f,
    converters,
    filter_funcs,
    # graphing,
    # pretty_sql,
    # joins,
    display,
)
from .. import config

def list_queries(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_list = config['DBSession'].query(StoredQuery).filter(StoredQuery.creator == the_user.id).order_by(StoredQuery.name.asc())
    
    return dict(
        title      = "Concision queries",
        layout     = layout,
        the_user   = the_user,
        query_list = query_list,
    )

def new(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    if "form.submitted" in request.params:
        the_query = StoredQuery()
        the_query.name = request.params['name'].strip()
        the_query.creator = the_user.id
        the_query.data = json.dumps(query_f.check_query_data({}))
        
        config['DBSession'].add(the_query)
        
        q = config['DBSession'].query(StoredQuery.id).filter(StoredQuery.creator == the_query.creator).order_by(StoredQuery.id.desc()).first()[0]
        return HTTPFound(location=request.route_url("concision.query.overview", query_id=q))
    
    return dict(
        title    = "Query name",
        layout   = layout,
        the_user = the_user,
    )

def overview(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    tablist = display.tablist(data)
    
    seletable_columns = []
    for t in data['tables']:
        the_source = config['sources'][t]
        seletable_columns.extend([("%s.%s" % (t, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    filter_html = display.filter_html(data['filters']).replace("[query_id]", str(query_id))
    
    # Grouping by
    selected_columns = defaultdict(list)
    for s in data['tables']:
        prelude = lambda c: '%s.%s' % (s, c) in data.get('columns', []) or '%s.%s' % (s, c) == data.get('key', "")
        
        the_source = config['sources'][s]
        selected_columns[s] = list(filter(prelude, the_source.columns))
    
    return dict(
        title       = "Concision query",
        layout      = layout,
        the_user    = the_user,
        the_query   = the_query,
        data        = data,
        tables      = list(display.tables(data)),
        columns     = list(display.columns(data)),
        filter_html = filter_html,
        orderbys    = list(display.orderbys(data)),
        query_key   = display.query_key(data),
        query_id    = query_id,
        
        tablist = tablist,
        seletable_columns = seletable_columns,
        
        html_f = html_f,
        consts = consts,
    )

def tables(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    seletable_tables = {}
    for k, s in config['sources'].items():
        if k in data['tables']: continue
        seletable_tables[k] = s.label
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        tables   = display.tables(data),
        
        seletable_tables = seletable_tables,
        
        html_f    = html_f,
        consts    = consts,
        query_id  = query_id,
    )

def columns(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    seletable_columns = []
    for t in data['tables']:
        the_source = config['sources'][t]
        seletable_columns.extend([("%s.%s" % (t, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        columns   = display.columns(data),
        
        seletable_columns = seletable_columns,
        
        html_f    = html_f,
        consts    = consts,
        query_id  = query_id,
    )

def filters(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    seletable_filters = []
    for t in data['tables']:
        the_source = config['sources'][t]
        seletable_filters.extend([("%s.%s" % (t, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    filter_html = display.filter_html(data['filters']).replace("[query_id]", str(query_id))
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        # filters   = display.filters(data),
        filter_html = filter_html,
        
        seletable_filters = seletable_filters,
        
        html_f    = html_f,
        consts    = consts,
        query_id  = query_id,
    )

def orderby(request):
    pass

def groupby(request):
    pass

def graphing(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    keyable_columns = []
    for t in data['tables']:
        the_source = config['sources'][t]
        keyable_columns.extend([("%s.%s" % (t, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.keys])
    
    selected_key = None
    if data['key'] != None:
        f, t, c = converters.get_parts(data['key'])
        selected_key = "{}.{}".format(t, c)
        funcs = f
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        # filters   = display.filters(data),
        
        keyable_columns = keyable_columns,
        selected_key = selected_key,
        
        html_f    = html_f,
        consts    = consts,
        query_id  = query_id,
    )
