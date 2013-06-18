import datetime
from sqlalchemy import func, or_
from sqlalchemy.orm import aliased
import json

from collections import defaultdict
from ...core.lib import common
from ...core.models import (
    DBSession,
    User,
)

from . import exporter

def convert(results, c_query, table_headers):
    series = []
    
    for h in table_headers[1:]:
        series.append({
            "name": h,
            "pointInterval": int(datetime.timedelta(days=1).total_seconds() * 1000),
            "data": [],
        })
    
    first_key = None
    for ri, r in enumerate(results):
        if first_key == None:
            first_key = r[0]
        
        for i, c in enumerate(r):
            if i == 0: continue
            # series[i-1]['data'].append(c)
            
            series[i-1]['data'].append({
                "name": r[0].strftime("%d/%m/%Y"),
                "y": c,
                "x": r[0],
            })
    
    json_series = json.dumps(series, default=exporter.json_export)
    json_series = exporter.graph_convert(json_series)
    
    # print("\n\n")
    # print(json_series)
    # print(first_key)
    # print("\n\n")
    
    data = {
        "start_date": "Date.UTC({0.year}, {0.month}, {0.day})".format(first_key),
        "series": json_series,
    }
    
    return data
