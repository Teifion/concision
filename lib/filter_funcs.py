from .. import config
from . import converters, consts

example_filters = {
    "type": "and",
    "id": 1,
    "contents": [{
        "type": "or",
        "id": 2,
        "contents": [
            {"column": "statline_outbound_qfup.agent", "operator": "=", "value": "value", "id":4},
            {"column": "statline_outbound_qfup.agent", "operator": "=", "value": "value", "id":5}
        ]},
        
        {"type": "and",
        "id": 3,
        "contents": [
            {"column": "statline_outbound_qfup.agent", "operator": "=", "value": "value", "id":6},
            {"column": "statline_outbound_qfup.agent", "operator": "=", "value": "value", "id":7}
        ]
    }]
}

def delete_filter(data, filter_id):
    new_data = dict(data)
    # prelude = lambda d: d['id'] != filter_id
    
    contents = []
    for item in data['contents']:
        if item['id'] != filter_id:
            if 'type' in item:
                contents.append(delete_filter(item, filter_id))
            else:
                contents.append(item)
    
    new_data['contents'] = contents
    return new_data

# print(example_filters)
# print("\n\n")
# print(delete_filter(example_filters,2))

group_template = """
"""
def _filter_group(data):
    "AND, OR"
    
    results = []
    results.append("<div class='filter_group' id='group_%s'>" % data['id'])
    
    if data['id'] != 1:
        results.append("<a href='../do_filter/[query_id]?action=delete&amp;filter=%s' class='del_link'>&nbsp;x&nbsp;</a>" % data['id'])
    results.append(" <span class='add_link' onclick='new_item(%s);'>&nbsp;+&nbsp;</span>" % data['id'])
    results.append(" <span class='add_group_link' onclick='new_group(%s);'>&nbsp;...&nbsp;</span>" % data['id'])
    results.append(" &nbsp; <span class='group_type'>%s</span>" % data['type'])
    
    for item in data['contents']:
        if 'type' in item:
            results.append(_filter_group(item))
        else:
            results.append(_filter_item(item))
    
    results.append("</div>")
    return "".join(results)

item_template = """
<a href="../do_filter/[query_id]?action=delete&amp;filter={item_id}" class="del_link">&nbsp;x&nbsp;</a>
&nbsp;&nbsp;
{table} {column}

&nbsp;&nbsp;
&#8594;
&nbsp;&nbsp;

{operator}

&nbsp;&nbsp;
&#8594;
&nbsp;&nbsp;

{value}
"""
def _filter_item(data):
    "Single filter operator"
    
    results = []
    results.append("<div class='filter_item'>")
    
    funcs, table, column = converters.get_parts(data['column'])
    func_labels = map(
        lambda k: consts.all_funcs[k],
        funcs,
    )
    
    source = config['sources'][table]
    results.append(item_template.format(
        table = source.label,
        column = "%s %s" % (" ".join(func_labels), source.column_labels[column]),
        operator = consts.operators[data['operator']],
        value = data['value'],
        item_id = data['id'],
    ))
    
    results.append("</div>")
    return "".join(results)
