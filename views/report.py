from pyramid.httpexceptions import HTTPFound
# from pyramid.response import Response
from collections import defaultdict

from pyramid.renderers import get_renderer

from ..models import (
    ConcisionReport,
)

import json

from ..lib import (
    html_f,
    consts,
    report_f,
    converters,
    filter_funcs,
    # graphing,
    # pretty_sql,
    # joins,
    report_display,
)
from .. import config

def list_reports(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    report_list = config['DBSession'].query(ConcisionReport).filter(ConcisionReport.creator == the_user.id).order_by(ConcisionReport.name.asc())
    
    return dict(
        title      = "Concision reports",
        layout     = layout,
        the_user   = the_user,
        report_list = report_list,
    )

def new(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    if "form.submitted" in request.params:
        the_report = ConcisionReport()
        the_report.name = request.params['name'].strip()
        the_report.creator = the_user.id
        the_report.data = json.dumps(report_f.check_report_data({}))
        
        config['DBSession'].add(the_report)
        
        q = config['DBSession'].query(ConcisionReport.id).filter(ConcisionReport.creator == the_report.creator).order_by(ConcisionReport.id.desc()).first()[0]
        return HTTPFound(location=request.route_url("concision.report.overview", report_id=q))
    
    return dict(
        title    = "Report name",
        layout   = layout,
        the_user = the_user,
    )

def overview(request):
    layout   = get_renderer(config['layout']).implementation()
    
    report_id = int(request.matchdict['report_id'])
    the_report = config['DBSession'].query(ConcisionReport).filter(ConcisionReport.id == report_id).first()
    data = the_report.extract_data()
    report_f.check_report_data(data)
    
    tablist = report_display.tablist(data)
    
    # seletable_columns = []
    # for t in data['tables']:
    #     the_source = config['sources'][t]
    #     seletable_columns.extend([("%s.%s" % (t, c), "%s %s" % (the_source.label, the_source.column_labels.get(c, c))) for c in the_source.columns])
    
    # filter_html = display.filter_html(data['filters']).replace("[report_id]", str(report_id))
    
    # # Grouping by
    # selected_columns = defaultdict(list)
    # for s in data['tables']:
    #     prelude = lambda c: '%s.%s' % (s, c) in data.get('columns', []) or '%s.%s' % (s, c) == data.get('key', "")
        
    #     the_source = config['sources'][s]
    #     selected_columns[s] = list(filter(prelude, the_source.columns))
    
    return dict(
        title       = "Concision query",
        layout      = layout,
        # the_user    = the_user,
        # the_report   = the_report,
        # data        = data,
        # tables      = list(display.tables(data)),
        # columns     = list(display.columns(data)),
        # filter_html = filter_html,
        # orderbys    = list(display.orderbys(data)),
        # query_key   = display.query_key(data),
        report_id    = report_id,
        
        tablist = tablist,
        # seletable_columns = seletable_columns,
        
        # html_f = html_f,
        # consts = consts,
    )