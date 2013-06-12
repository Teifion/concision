import datetime
import decimal
import json

def convert_value(v):
    if v is None: return None
    
    if type(v) == datetime.datetime:
        return v.strftime("%H:%M:%S %d/%m/%Y")
    
    if type(v) == datetime.date:
        return v.strftime("%d/%m/%Y")
    
    if type(v) in (int, str, float, decimal.Decimal):
        return v
    
    raise KeyError("No handler for data of type %s" % type(v))

def convert(row):
    return list(map(convert_value, row))

def json_export(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%H:%M %d/%m/%Y")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%d/%m/%Y")
    elif isinstance(obj, decimal.Decimal):
        return float(str(obj))
    else:
        return obj
