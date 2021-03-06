# import transaction
# import datetime
import io
import csv
from collections import defaultdict

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

import json
from ..lib import html_f, consts, query_f, exporter, graphing, pretty_sql, joins
from .. import config

def new_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    return dict(
        title    = "Query name",
        layout   = layout,
        the_user = the_user,
    )

def add_new_query(request):
    the_user = config['get_user_func'](request)
    
    if "form.submitted" in request.params:
        the_query = StoredQuery()
        the_query.name = request.params['name'].strip()
        the_query.creator = the_user.id
        the_query.data = json.dumps(query_f.check_query_data({}))
        
        config['DBSession'].add(the_query)
        
        q = config['DBSession'].query(StoredQuery.id).filter(StoredQuery.creator == the_query.creator).order_by(StoredQuery.id.desc()).first()[0]
        return HTTPFound(location=request.route_url("concision.query.source", query_id=q))
    return HTTPFound(location=request.route_url("concision.query.new"))

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

def edit_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    query_f.check_query_data(data)
    
    # Columns
    relevant_sources = [s for s in config['sources'].items() if s[0] in data['sources']]
    existing_columns = data.get('columns', [])
    
    # Filters
    columns = []
    for s in data['sources']:
        the_source = config['sources'][s]
        columns.extend([("%s.%s" % (s, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    # Group by
    selected_columns = defaultdict(list)
    for s in data['sources']:
        prelude = lambda c: '%s.%s' % (s, c) in data.get('columns', []) or '%s.%s' % (s, c) == data.get('key', "")
        
        the_source = config['sources'][s]
        selected_columns[s] = list(filter(prelude, the_source.columns))
    
    # Joins
    current_source_joins = joins.current_source_joins(data)
    possible_source_joins = joins.possible_source_joins(data)
    
    return dict(
        title     = "Concision query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        data      = data,
        columns = columns,
        sources   = config['sources'],
        selected_columns = selected_columns,
        relevant_sources = relevant_sources,
        
        current_source_joins = current_source_joins,
        possible_source_joins = possible_source_joins,
        
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

def raw_query(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    query_id = int(request.matchdict['query_id'])
    the_query = config['DBSession'].query(StoredQuery).filter(StoredQuery.id == query_id).first()
    data = the_query.extract_data()
    
    results, c_query = query_f.build(data)
    
    explain   = []
    the_query = ""
    
    if results != []:
        the_query = pretty_sql.prettify(results)
        
        raw_query = pretty_sql.compile_query(results)
        explain = []
        for e in config['DBSession'].execute("EXPLAIN ANALYZE %s" % raw_query):
            explain.append(str(e[0]))
    else:
        the_query = "No columns selected"
    
    return dict(
        title     = "Raw query",
        layout    = layout,
        the_user  = the_user,
        the_query = the_query,
        explain   = "\n".join(explain),
        query_id  = query_id,
        data      = data,
    )

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
