# import transaction
# import datetime

from pyramid.renderers import get_renderer
from pyramid.renderers import render_to_response

# from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import get_renderer

# from ..lib import ()

from ..models import (
    StoredQuery,
)

from .. import config

def doc_menu(request):
    the_user = config['get_user_func'](request)
    layout   = get_renderer(config['layout']).implementation()
    
    return dict(
        title           = "Concision documentation",
        layout          = layout,
    )

def doc_page(request):
    page = request.matchdict['page']
    layout   = get_renderer(config['layout']).implementation()
    
    return render_to_response("../templates/documentation/{}.pt".format(page),
        dict(
            title  = 'Concision documentation',
            layout = layout,
        ),
        request = request,
    )

def tooltip(request):
    page   = request.matchdict['page']
    request.do_not_log = True
    
    try:
        return render_to_response("../templates/documentation/tooltips/{}.pt".format(page),
            {},
            request = request,
        )
    except ValueError:
        return render_to_response("../templates/documentation/tooltips/tooltip_404.pt",
            {},
            request = request,
        )
    
