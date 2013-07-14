from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

import io
import csv

from ..lib import (
    # html_f,
    # consts,
    exporter,
    query_f,
    converters,
    graphing,
    pretty_sql,
    # joins,
    display,
)
from .. import config

def view(request):
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
        f, t, c = converters.get_parts(tc)
        table_headers.append(config['sources'][t].column_labels.get(c, c))
    
    return dict(
        title    = "Concision query",
        layout   = layout,
        the_user = the_user,
        
        c_query  = c_query,
        results  = results,
        data     = data,
        query_id = query_id,
        tablist = display.tablist(data),
        
        table_headers = table_headers,
    )

def graph(request):
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
        f, t, c = converters.get_parts(tc)
        table_headers.append(config['sources'][t].column_labels.get(c, c))
    
    try:
        graph_data = graphing.convert(results, c_query, table_headers)
    except Exception:
        graph_data = {}
    
    return dict(
        title    = "Concision query",
        layout   = layout,
        the_user = the_user,
        
        c_query  = c_query,
        results  = results,
        data     = data,
        query_id = query_id,
        tablist = display.tablist(data),
        
        graph_data = graph_data,
        
        # table_headers = table_headers,
    )

def export(request):
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

def raw(request):
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
        tablist = display.tablist(data),
    )

def delete(request):
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
