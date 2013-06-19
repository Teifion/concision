from sqlalchemy import func
from collections import defaultdict

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

operator_converters = defaultdict(lambda v: v)

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

group_lookup = {
    "SUM": func.sum,
    "AVG": func.avg,
    "MAX": func.max,
    "MIN": func.min,
    "COUNT": func.count,
    "ARRAY": func.array_agg,
}

orderby = {
    "ASC": "Ascending (0 to 9, A to Z)",
    "DESC": "Descending (9 to 0, Z to A)",
}
