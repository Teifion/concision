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

def get_max_id(data, current_max=1):
    for item in data['contents']:
        if 'type' in item:
            current_max = max(get_max_id(item, current_max), current_max)
        else:
            current_max = max(item['id'], current_max)
    
    return current_max

def get_columns(data):
    columns = []
    
    for item in data['contents']:
        if 'type' in item:
            columns.extend(get_columns(item))
        else:
            columns.append(item['column'])
    
    return columns

def add_item(data, filter_id, new_item):
    new_data = dict(data)
    
    contents = []
    # if filter_id == data['id']:
    #     contents.append(new_item)
    for item in data['contents']:
        if 'type' in item:
            contents.append(add_item(item, filter_id, new_item))
        else:
            contents.append(item)
    
    if data['id'] == filter_id:
        contents.append(new_item)
    
    new_data['contents'] = contents
    return new_data

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

def build(the_query, data):
    f = consts.filter_lookup[data['type']]
    
    parts = []
    for item in data['contents']:
        if 'type' in item:
            parts.append(build(the_query, item))
        else:
            parts.append(build_compare(the_query, item))
    
    return f(*parts)

def build_compare(the_query, item):
    filter_col = the_query.get(item['column'], pure=True)
    op_func = getattr(filter_col, consts.operator_lookup[item['operator']])
    
    funcs, t, c = converters.get_parts(item['column'])
    source_table = config['sources'][t]
    # config['sources'][table]
    # if column in table_source.aliases:
    
    value = item['value']
    
    # Enum?
    if c in source_table.enums:
        if value in source_table.enums[c]:
            value = source_table.enums[c].index(value)
        else:
            raise Exception("")
    
    # Convert it from a string into the relevant database type
    value = converters.typecast(the_query.get(item['column'], use_alias=False, pure=True), value)
    
    # Apply conversion functions to it
    value = converters.convert(value, source_table.column_converters.get(c, []))
    
    # Apply filter type converts to it
    value = consts.operator_converters[item['operator']](value)
    
    return op_func(value)

# print("\n\n")
# print(build(example_filters))
# print("\n\n")
