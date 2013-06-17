from sqlalchemy import func

operators = {
    "=": "equal to",
    "!=": "not equal to",
    ">": "greater than",
    ">=": "greater than or equal to",
    "<": "less than",
    "<=": "less than or equal to",
}

operator_lookup = {
    ">":  "__gt__",
    ">=": "__ge__",
    
    "<":  "__lt__",
    "<=": "__le__",
    
    "=":  "__eq__",
    "!=": "__ne__",
}

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
