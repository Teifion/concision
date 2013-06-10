import json
from decimal import Decimal
from .. import config
from sqlalchemy.orm import aliased
import datetime
import re
from . import converters, html_f, consts

from sqlalchemy.types import (
    Integer as sql_integer,
    Numeric as sql_numeric,
    String as sql_string,
    Date as sql_date,
    DateTime as sql_datetime,
)

class CQuery(object):
    """An object for storing the query being built."""
    
    def __init__(self):
        super(CQuery, self).__init__()
        self.aliases = {}
        
        self.columns   = []
        self.filters   = []
        self.order_bys = []
        self.group_bys = []
            
    def check_for_aliases(self, data):
        """
        Goes through all referenced fields and checks to see if they
        are in the alias list. Any it finds it adds aliases for and 
        extends the filters so the alias will be linked to.
        """
        total_columns = data['columns'] + [data['key']] + [f['column'] for f in data['filters']]
        
        for table_column in filter(None, total_columns):
            t, c = table_column.split(".")
            table = config['sources'][t]
            
            if c in table.aliases:
                the_alias = table.aliases[c]
                
                # We don't want to make the same alias twice
                if the_alias['name'] in self.aliases:
                    continue
                
                # Create the alias
                alias_class = the_alias['db_class']
                alias_instance = aliased(alias_class, name=the_alias['name'])
                self.aliases[the_alias['name']] = alias_instance
                
                # Link the alias with a filter
                local_column = config['metadata'].tables[t].columns[c]
                alias_column = getattr(alias_instance, the_alias['join_on'])
                
                self.filters.append(local_column == alias_column)
    
    def get(self, identifier, use_alias=True):
        """
        Grabs a column or an alias of a column if it's meant to be using one.
        """
        table, column = identifier.split('.')
        table_source = config['sources'][table]
        
        # First check if it's an alias
        if column in table_source.aliases:
            the_alias = table_source.aliases[column]
            
            if use_alias:
                alias_table = self.aliases[the_alias['name']]
                return getattr(alias_table, the_alias['column'])
            
            # We're not using the table alias because the
            # version of SQLAlchemy for zope doesn't have what we need
            # instead we're going to get the actual target of the alias
            # rather than the aliased target
            target_table = the_alias['table']
            target_column = the_alias['column']
            
            return config['metadata'].tables[target_table].columns[target_column]
         
        # If not then grab the column itself
        return config['metadata'].tables[table].columns[column]

template_re = re.compile(r"\{[a-zA-Z0-9_]+\}")
def apply_template(value):
    if "{today}" in value:
        value = value.replace("{today}", datetime.date.today().strftime("%d/%m/%Y"))
    
    if "{yesterday}" in value:
        today = datetime.date.today()
        value = value.replace("{yesterday}", (today - datetime.timedelta(days=1)).strftime("%d/%m/%Y"))
    
    if template_re.search(value):
        raise ValueError("Template item still remaining in '%s'" % value)
    
    return value

def typecast(filter_col, value):
    """
    Converts the value from a string into the correct datatype
    for the database.
    """
    # dat = []
    # dat.append(str(dir(filter_col)))
    # for d in dir(filter_col):
    #     dat.append("%s: %s" % (d, getattr(filter_col, d)))
    # raise Exception("\n\n".join(dat))
    
    ptype = type(filter_col.type)
    value = apply_template(value)
    
    if ptype == sql_date:
        try:
            d, m, y = value.split("/")
        except Exception as e:
            raise e
        
        return datetime.date(year=int(y), month=int(m), day=int(d))
        
    elif ptype == sql_datetime:
        # TODO: Accept times as well as just dates
        d, m, y = value.split("/")
        return datetime.datetime(year=int(y), month=int(m), day=int(d))
    
    elif ptype == sql_numeric:
        return Decimal(value)
    elif ptype == sql_integer:
        return int(value)
    elif ptype == sql_string:
        return value
    else:
        raise KeyError("No handler for %s" % ptype)

def build(data):
    q = CQuery()
    q.check_for_aliases(data)
    
    # columns
    if data['key'] != None:
        q.columns.append(q.get(data['key']))
    
    for c in data['columns']:
        q.columns.append(q.get(c))
    
    # Filters
    for f in data['filters']:
        filter_col = q.get(f['column'])
        op_func = getattr(filter_col, consts.operator_lookup[f['operator']])
        
        t, c = f['column'].split(".")
        source_table = config['sources'][t]
        # config['sources'][table]
        # if column in table_source.aliases:
        
        value = converters.convert(f['value'], source_table.column_converters.get(c))
        # value = convert_value(f['value'], [])
        
        value = typecast(q.get(f['column'], use_alias=False), value)
        
        q.filters.append(op_func(value))
    
    # TODO desc/asc
    if data['key'] != None:
        q.order_bys.append(q.get(data['key']))
    
    if len(q.columns) == 0:
        return [], q
    
    return config['DBSession'].query(*q.columns).filter(*q.filters).order_by(*q.order_bys).group_by(*q.group_bys).limit(200), q

def check_query_data(data):
    data['key'] = data.get('key', None)
    data['columns'] = data.get('columns', [])
    data['filters'] = data.get('filters', [])
    return data
