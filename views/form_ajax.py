# import transaction
# import datetime

from pyramid.httpexceptions import HTTPFound

# from pyramid.renderers import get_renderer

from ..models import (
    StoredQuery,
)

# import json
from ..lib import (
    query_f,
    converters,
)
from .. import config

def function_dropdown(request):
    request.do_not_log = True
    
    funcs, table, column = converters.get_parts(request.matchdict['column'])
    
    the_source = config['sources'][table]
    the_column = the_source.table
    
    return "XXXYYYYZZ"
