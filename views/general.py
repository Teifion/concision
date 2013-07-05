# import transaction
# import datetime

# from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import get_renderer

# from ..lib import ()

from ..models import (
    StoredQuery,
)

from .. import config

def menu(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    return dict(
        title           = "Concision menu",
        layout          = layout,
        the_user        = the_user,
    )

def preferences(request):
    pass
