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

def graph_user(start_date, end_date, user, **ignore):
    user_id = DBSession.query(User.id).filter(User.name == user.upper().strip()).first()[0]
    
    series = []
    
    the_date_trunc = func.date_trunc('day', SMSReceived.date_received)
    fields = [
        the_date_trunc,
        func.count(SMSReceived.id),
        func.avg(SMSReceived.agent_score),
        func.avg(SMSReceived.service_score),
        func.avg(SMSReceived.first_time),
    ]
    
    filters = [
        SMSReceived.ignore == False,
        SMSReceived.agent == user_id,
        the_date_trunc > start_date,
        the_date_trunc < end_date,
    ]
    
    order_by = [
        the_date_trunc
    ]
    
    sent_date_trunc = func.date_trunc('day', SMSSent.the_date)
    sent_data = reports.get_sent_amounts(start_date, end_date, "datetrunc", user=user_id, datetrunc=sent_date_trunc)
    
    data = defaultdict(list)
    for d in DBSession.query(*fields).filter(*filters).order_by(*order_by).group_by(the_date_trunc):
        data['service_score'].append(float(round(d[2], 2)))
        data['agent_score'].append(float(round(d[3], 2)))
        data['first_time'].append(float(round(d[4], 3)*10))
        
        sent, rec = sent_data.get(d[0].strftime("%Y/%m/%d"), (1,0))
        data['response_rate'].append(round((rec/sent)*100,2))
    
    series.append(new_series("Service score", data['service_score']))
    series.append(new_series("Agent score",   data['agent_score']))
    series.append(new_series("FCR",           data['first_time']))
    series.append(new_series("Response rate", data['response_rate']))
    
    return {
        "series": json.dumps(series),
        "start_date": start_date.strftime("Date.UTC(%Y, %m, %d)")
    }