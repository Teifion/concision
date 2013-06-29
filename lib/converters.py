import datetime
import re
from decimal import Decimal

from sqlalchemy.types import (
    Integer as sql_integer,
    Numeric as sql_numeric,
    Float as sql_float,
    String as sql_string,
    Date as sql_date,
    DateTime as sql_datetime,
)

func_dict = {
    "upper": lambda v: v.upper(),
    "strip": lambda v: v.strip(),
}

def convert(value, funcs):
    for f in [func_dict[fname] for fname in funcs]:
        value = f(value)
    return value

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
    
    ptype = type(filter_col.type)
    
    if isinstance(value, str):
        value = apply_template(value)
    
    if ptype == sql_date:
        temp_value = value.replace(" ", "/").replace("-", "/")
        d, m, y = temp_value.split("/")
        
        if int(y) < 1000: y = 2000 + int(y)
        
        return datetime.date(year=int(y), month=int(m), day=int(d))
        
    elif ptype == sql_datetime:
        # TODO: Accept times as well as just dates
        temp_value = value.replace(" ", "/").replace("-", "/")
        d, m, y = temp_value.split("/")
        return datetime.datetime(year=int(y), month=int(m), day=int(d))
    
    elif ptype == sql_numeric:
        return Decimal(value)
    elif ptype == sql_integer:
        return int(value)
    elif ptype == sql_float:
        return float(value)
    elif ptype == sql_string:
        return value
    else:
        raise KeyError("No handler for %s" % ptype)
