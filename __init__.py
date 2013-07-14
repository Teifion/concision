config = {
    "layout":     "../templates/default_layout.pt",
    "metadata":   None,
    "DBSession":  None,
    
    "limit":      400,
    
    "sources":    {},
    "get_userid": lambda r: KeyError("No function exists to get the userid"),
}

def add_source(the_source):
    if the_source.name in config['sources']:
        return
        raise KeyError("{} already exists as a source".format(the_source.name))
    
    config['sources'][the_source.name] = the_source

def example_config_constructor(config):
    """This is an example of how I'm setting up my Concision configuration"""
    
    from . import concision as concision
    from . import models
    
    config.include(concision)
    concision.config['layout']        = '../../templates/layouts/viewer.pt'
    concision.config['DBSession']     = DBSession
    concision.config['metadata']      = models.Base.metadata
    concision.config['get_userid']    = lambda r: r.user.id
    concision.config['get_user_func'] = lambda r: r.user
    
    from .concision import example_sources
    concision.add_source(example_sources.stat_table)

def includeme(config):
    report_views(config)
    
    from .views import query as query
    from .views import forms as forms
    from .views import documentation as docs
    from .views import general as general
    from .views import form_ajax as form_ajax
    from .views import query_view as query_view
    
    # Standard views
    config.add_route('concision.menu', '/concision/menu')
    config.add_route('concision.preferences', '/concision/preferences')
    config.add_route('concision.list_queries', '/concision/queries/list')
    
    config.add_view(general.menu, route_name='concision.menu',
        renderer='templates/general/menu.pt', permission='concision')
    config.add_view(general.preferences, route_name='concision.preferences',
        renderer='templates/general/preferences.pt', permission='concision')
    config.add_view(query.list_queries, route_name='concision.list_queries',
        renderer='templates/general/list_queries.pt', permission='concision')
    
    # Queries
    config.add_route('concision.query.new', '/concision/query/new')
    config.add_route('concision.query.add_new', '/concision/query/add_new')
    config.add_route('concision.query.overview', '/concision/query/overview/{query_id}')
    config.add_route('concision.query.delete', '/concision/query/delete/{query_id}')
    config.add_route('concision.query.view', '/concision/query/view/{query_id}')
    config.add_route('concision.query.graph', '/concision/query/graph/{query_id}')
    config.add_route('concision.query.export', '/concision/query/export/{query_id}')
    config.add_route('concision.query.raw', '/concision/query/raw/{query_id}')
    
    config.add_view(query.new, route_name='concision.query.new', renderer='templates/queries/new.pt', permission='concision_edit')
    config.add_view(query.new, route_name='concision.query.add_new', renderer='templates/queries/new.pt', permission='concision_edit')
    config.add_view(query.overview, route_name='concision.query.overview', renderer='templates/queries/overview.pt', permission='concision_edit')
    config.add_view(query_view.view, route_name='concision.query.view', renderer='templates/queries/view.pt', permission='concision')
    config.add_view(query_view.graph, route_name='concision.query.graph', renderer='templates/queries/graph.pt', permission='concision')
    config.add_view(query_view.export, route_name='concision.query.export', permission='concision')
    config.add_view(query_view.raw, route_name='concision.query.raw', renderer='templates/queries/raw.pt', permission='concision')
    config.add_view(query_view.delete, route_name='concision.query.delete', renderer='templates/queries/delete.pt', permission='concision_edit')
    
    # Tables
    config.add_route('concision.query.tables', '/concision/query/tables/{query_id}')
    config.add_route('concision.query.do_table', '/concision/query/do_table/{query_id}')
    
    config.add_view(query.tables, route_name='concision.query.tables', renderer='templates/queries/tables.pt', permission='concision_edit')
    config.add_view(forms.table, route_name='concision.query.do_table', permission='concision_edit')
    
    # Columns
    config.add_route('concision.query.columns', '/concision/query/columns/{query_id}')
    config.add_route('concision.query.do_column', '/concision/query/do_column/{query_id}')
    
    config.add_view(query.columns, route_name='concision.query.columns', renderer='templates/queries/columns.pt', permission='concision_edit')
    config.add_view(forms.column, route_name='concision.query.do_column', permission='concision_edit')
    
    # Filters
    config.add_route('concision.query.filters', '/concision/query/filters/{query_id}')
    config.add_route('concision.query.do_filter', '/concision/query/do_filter/{query_id}')
    
    config.add_view(query.filters, route_name='concision.query.filters', renderer='templates/queries/filters.pt', permission='concision_edit')
    config.add_view(forms.filters, route_name='concision.query.do_filter', permission='concision_edit')
    
    # Order By
    config.add_route('concision.query.orderby', '/concision/query/orderby/{query_id}')
    config.add_route('concision.query.do_orderby', '/concision/query/do_orderby/{query_id}')
    
    config.add_view(query.orderby, route_name='concision.query.orderby', renderer='templates/queries/orderby.pt', permission='concision_edit')
    config.add_view(forms.orderby, route_name='concision.query.do_orderby', permission='concision_edit')
    
    # Group By
    config.add_route('concision.query.groupby', '/concision/query/groupby/{query_id}')
    config.add_route('concision.query.do_groupby', '/concision/query/do_groupby/{query_id}')
    
    config.add_view(query.groupby, route_name='concision.query.groupby', renderer='templates/queries/groupby.pt', permission='concision_edit')
    config.add_view(forms.groupby, route_name='concision.query.do_groupby', permission='concision_edit')
    
    # Graphing
    config.add_route('concision.query.graphing', '/concision/query/graphing/{query_id}')
    config.add_route('concision.query.do_key', '/concision/query/do_key/{query_id}')
    
    config.add_view(query.graphing, route_name='concision.query.graphing', renderer='templates/queries/graphing.pt', permission='concision_edit')
    config.add_view(forms.do_key, route_name='concision.query.do_key', permission='concision_edit')
    
    # Other
    config.add_route('concision.query.do_other', '/concision/query/do_other/{query_id}')
    
    config.add_view(forms.other, route_name='concision.query.do_other', permission='concision_edit')
    
    # Ajax
    config.add_route('concision.ajax.function_dropdown', '/concision/ajax/function_dropdown')
    config.add_view(form_ajax.function_dropdown, route_name='concision.ajax.function_dropdown', renderer='string', permission='concision_edit')
    
    # Documentation
    config.add_route('concision.doc.menu', '/concision/documentation/menu')
    config.add_route('concision.doc.page', '/concision/documentation/page/{page}')
    config.add_route('concision.tooltip', '/concision/tooltip/{page}')
    
    config.add_view(docs.doc_menu, route_name='concision.doc.menu',
        renderer='templates/documentation/menu.pt', permission='concision')
    config.add_view(docs.doc_page, route_name='concision.doc.page', permission='concision')
    config.add_view(docs.tooltip, route_name='concision.tooltip', renderer='string', http_cache=3600)
    
    return config

def report_views(config):
    from .views import report as report
    
    # Standard views
    config.add_route('concision.report.list', '/concision/report/list')
    config.add_route('concision.report.new', '/concision/report/new')
    config.add_route('concision.report.add_new', '/concision/report/add_new')
    config.add_route('concision.report.overview', '/concision/report/overview/{report_id}')
    
    config.add_view(report.list_reports, route_name='concision.report.list',
        renderer='templates/report/list.pt', permission='concision')
    config.add_view(report.new, route_name='concision.report.new',
        renderer='templates/report/new.pt', permission='concision')
    config.add_view(report.new, route_name='concision.report.add_new', renderer='templates/report/new.pt', permission='concision_edit')
    config.add_view(report.overview, route_name='concision.report.overview', renderer='templates/report/overview.pt', permission='concision_edit')
    
    # Queries
    config.add_route('concision.report.queries', '/concision/report/queries/{report_id}')
