# import transaction
# import datetime
import io
import csv

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

import json
from ..lib import html_f, consts, query_f, exporter, graphing
from .. import config

def new_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    if "form.submitted" in request.params:
        the_query = StoredQuery()
        the_query.name = request.params['name'].strip()
        the_query.creator = the_user.id
        the_query.data = json.dumps(query_f.check_query_data({}))
        
        config['DBSession'].add(the_query)
        
        q = config['DBSession'].query(StoredQuery.id).filter(StoredQuery.creator == the_query.creator).order_by(StoredQuery.id.desc()).first()[0]
        return HTTPFound(location=request.route_url("concision.query.source", query_id=q))
    
    return dict(
        title    = "Query name",
        layout   = layout,
        the_user = the_user,
    )

def source(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    
    if "form.submitted" in request.params:
        data = the_query.extract_data()
        data["mode"]   = request.params['mode']
        data["sources"] = [request.params['source']]
        query_f.check_query_data(data)
        the_query.compress_data()
        
        config['DBSession'].add(the_query)
        
        return HTTPFound(location=request.route_url("concision.query.edit", query_id=query_id))
    
    return dict(
        title             = "Query source",
        layout            = layout,
        the_query         = the_query,
        
        html_f            = html_f,
        single_sources    = {k:v for k, v in config['sources'].items() if v.query_as_single},
        aggregate_sources = {k:v for k, v in config['sources'].items() if v.query_as_aggregate},
    )

def columns(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    sources = [config['sources'][s] for s in data['sources']]
    existing_columns = data.get('columns', [])
    
    return dict(
        title            = "Query filters",
        layout           = layout,
        the_user         = the_user,
        
        html_f           = html_f,
        the_query        = the_query,
        qdata            = data,
        sources          = config['sources'],
        existing_columns = existing_columns,
    )

def filters(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    columns = []
    for s in data['sources']:
        the_source = config['sources'][s]
        columns.extend([("%s.%s" % (s, c),the_source.column_labels.get(c, c)) for c in the_source.columns])
    
    existing_filters = data.get('filters', [])
    
    return dict(
        title            = "Query filters",
        layout           = layout,
        the_user         = the_user,
        
        html_f           = html_f,
        the_query        = the_query,
        existing_filters = existing_filters,
        sources          = config['sources'],
        columns          = columns,
        operators        = consts.operators,
    )

def key(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    sources = [config['sources'][s] for s in data['sources']]
    existing_key = data.get('key', "")
    
    return dict(
        title            = "Query filters",
        layout           = layout,
        the_user         = the_user,
        
        html_f           = html_f,
        the_query        = the_query,
        qdata            = data,
        sources          = config['sources'],
        existing_key     = existing_key,
    )

def edit_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    # Columns
    existing_columns = data.get('columns', [])
    
    # Filters
    columns = []
    for s in data['sources']:
        the_source = config['sources'][s]
        columns.extend([("%s.%s" % (s, c),the_source.column_labels.get(c, c)) for c in the_source.columns])
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        columns = columns,
        sources   = config['sources'],
        
        html_f = html_f,
        consts = consts,
    )

def view_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    results, c_query = query_f.build(data)
    
    table_headers = []
    for tc in [data['key']] + data['columns']:
        if tc is None: continue
        t, c = tc.split(".")
        table_headers.append(config['sources'][t].column_labels.get(c, c))
    
    return dict(
        title    = "Concision query",
        layout   = layout,
        the_user = the_user,
        
        c_query  = c_query,
        results  = results,
        data     = data,
        query_id = query_id,
        
        table_headers = table_headers,
    )

def graph_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    if data['key'] is None:
        return HTTPFound(location=request.route_url("concision.query.view", query_id=query_id))
    
    results, c_query = query_f.build(data)
    
    table_headers = []
    for tc in [data['key']] + data['columns']:
        t, c = tc.split(".")
        table_headers.append(config['sources'][t].column_labels.get(c, c))
    
    graph_data = graphing.convert(results, c_query, table_headers)
    
    return dict(
        title    = "Concision query",
        layout   = layout,
        the_user = the_user,
        
        c_query  = c_query,
        results  = results,
        data     = data,
        query_id = query_id,
        
        graph_data = graph_data,
        
        # table_headers = table_headers,
    )

def export_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    results, c_query = query_f.build(data)
    
    table_headers = []
    for tc in filter(None, [data['key']] + data['columns']):
        t, c = tc.split(".")
        table_headers.append(config['sources'][t].column_labels.get(c, c))
    
    f = io.StringIO()
    w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    w.writerow(table_headers)
    
    for row in results:
        w.writerow(exporter.convert(row))
    
    f.seek(0)
    return Response(body=f.read(), content_type='text/plain', content_disposition='attachment; filename="concision_export.csv"')
    
    return f.read()

def delete_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    
    if the_query.creator != the_user.id:
        return HTTPFound(location=request.route_url("concision.menu"))
    
    if 'form.submitted' in request.params:
        config['DBSession'].delete(the_query)
        return HTTPFound(location=request.route_url("concision.menu"))
    
    return dict(
        title     = "Delete query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
    )
