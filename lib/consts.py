from sqlalchemy import func
from collections import defaultdict
from functools import partial

operators = {
    "=": "equal to",
    "!=": "not equal to",
    ">": "greater than",
    ">=": "greater than or equal to",
    "<": "less than",
    "<=": "less than or equal to",
    "in": "in list",
}

operator_lookup = {
    ">":  "__gt__",
    ">=": "__ge__",
    
    "<":  "__lt__",
    "<=": "__le__",
    
    "=":  "__eq__",
    "!=": "__ne__",
    
    "in": "in_",
}

def straight_value():
    def f(v):
        return v
    return f
operator_converters = defaultdict(straight_value)

# In takes a list of values
operator_converters['in'] = lambda v: [x.strip() for x in v.replace(",", "\n").split("\n")]

group_funcs = {
    "-": " Group by",
    "SUM": "Total",
    "AVG": "Average",
    "MAX": "Maximum",
    "MIN": "Minimum",
    "COUNT": "Count",
    "ARRAY": "Array",
}

non_group_funcs = {
    "DATE_TRUNC_YEAR": "Date truncation (Year)",
    "DATE_TRUNC_MONTH": "Date truncation (Month)",
    "DATE_TRUNC_DAY": "Date truncation (Day)",
}

all_funcs = dict(group_funcs)
for k, v in non_group_funcs.items(): all_funcs[k] = v

function_lookup = {
    "SUM": func.sum,
    "AVG": func.avg,
    "MAX": func.max,
    "MIN": func.min,
    "COUNT": func.count,
    "ARRAY": func.array_agg,
    
    "DATE_TRUNC_YEAR": partial(func.date_trunc, 'year'),
    "DATE_TRUNC_MONTH": partial(func.date_trunc, 'month'),
    "DATE_TRUNC_DAY": partial(func.date_trunc, 'day'),
}
# Used because we still have group_lookup in some places
group_lookup = function_lookup

orderby = {
    "ASC": "Ascending (0 to 9, A to Z)",
    "DESC": "Descending (9 to 0, Z to A)",
}
