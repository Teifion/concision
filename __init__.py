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

from . import views
def includeme(config):
    # Standard views
    config.add_route('concision.menu', '/concision/menu')
    config.add_route('concision.preferences', '/concision/preferences')
    config.add_route('concision.list_queries', '/concision/list/queries')
    
    # Querie edit/viewing
    config.add_route('concision.query.source', '/concision/query/source/{query_id}')
    config.add_route('concision.query.edit_columns', '/concision/query/edit_columns/{query_id}')
    config.add_route('concision.query.edit_groupby', '/concision/query/edit_groupby/{query_id}')
    
    config.add_route('concision.query.add_filter', '/concision/query/add_filter/{query_id}')
    config.add_route('concision.query.edit_filter', '/concision/query/edit_filter/{query_id}')
    config.add_route('concision.query.delete_filter', '/concision/query/delete_filter/{query_id}')
    
    config.add_route('concision.query.add_orderby', '/concision/query/add_orderby/{query_id}')
    config.add_route('concision.query.edit_orderby', '/concision/query/edit_orderby/{query_id}')
    config.add_route('concision.query.delete_orderby', '/concision/query/delete_orderby/{query_id}')
    
    config.add_route('concision.query.edit_key', '/concision/query/edit_key/{query_id}')
    
    config.add_route('concision.query.new', '/concision/query/new')
    config.add_route('concision.query.edit', '/concision/query/edit/{query_id}')
    config.add_route('concision.query.delete', '/concision/query/delete/{query_id}')
    config.add_route('concision.query.view', '/concision/query/view/{query_id}')
    config.add_route('concision.query.graph', '/concision/query/graph/{query_id}')
    config.add_route('concision.query.export', '/concision/query/export/{query_id}')
    config.add_route('concision.query.raw', '/concision/query/raw/{query_id}')
    
    # Now add the views
    config.add_view(views.menu, route_name='concision.menu',
        renderer='templates/general/menu.pt', permission='concision')
    config.add_view(views.preferences, route_name='concision.preferences',
        renderer='templates/general/preferences.pt', permission='concision')
    config.add_view(views.list_queries, route_name='concision.list_queries',
        renderer='templates/general/list_queries.pt', permission='concision')
    
    config.add_view(views.source, route_name='concision.query.source',
        renderer='templates/queries/source.pt', permission='concision_edit')
    
    config.add_view(views.edit_columns, route_name='concision.query.edit_columns', permission='concision_edit')
    config.add_view(views.edit_groupby, route_name='concision.query.edit_groupby', permission='concision_edit')
    
    config.add_view(views.edit_key, route_name='concision.query.edit_key', permission='concision_edit')
    
    config.add_view(views.add_filter, route_name='concision.query.add_filter', permission='concision_edit')
    config.add_view(views.edit_filter, route_name='concision.query.edit_filter', permission='concision_edit')
    config.add_view(views.delete_filter, route_name='concision.query.delete_filter', permission='concision_edit')
    
    config.add_view(views.add_orderby, route_name='concision.query.add_orderby', permission='concision_edit')
    config.add_view(views.edit_orderby, route_name='concision.query.edit_orderby', permission='concision_edit')
    config.add_view(views.delete_orderby, route_name='concision.query.delete_orderby', permission='concision_edit')
    
    config.add_view(views.new_query, route_name='concision.query.new',
        renderer='templates/queries/new.pt', permission='concision_edit')
    config.add_view(views.edit_query, route_name='concision.query.edit',
        renderer='templates/queries/edit.pt', permission='concision_edit')
    config.add_view(views.view_query, route_name='concision.query.view',
        renderer='templates/queries/view.pt', permission='concision')
    config.add_view(views.graph_query, route_name='concision.query.graph',
        renderer='templates/queries/graph.pt', permission='concision')
    config.add_view(views.export_query, route_name='concision.query.export', permission='concision')
    config.add_view(views.raw_query, route_name='concision.query.raw',
        renderer='templates/queries/raw.pt', permission='concision')
    config.add_view(views.delete_query, route_name='concision.query.delete',
        renderer='templates/queries/delete.pt', permission='concision_edit')
    
    # Documentation
    config.add_route('concision.doc.menu', '/concision/documentation/menu')
    config.add_route('concision.doc.page', '/concision/documentation/page/{page}')
    config.add_route('concision.tooltip', '/concision/tooltip/{page}')
    
    config.add_view(views.doc_menu, route_name='concision.doc.menu',
        renderer='templates/documentation/menu.pt', permission='concision')
    config.add_view(views.doc_page, route_name='concision.doc.page', permission='concision')
    config.add_view(views.tooltip, route_name='concision.tooltip', renderer='string', http_cache=3600)
    
    return config
