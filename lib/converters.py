func_dict = {
    "upper": lambda v: v.upper(),
    "strip": lambda v: v.strip(),
}

def convert(value, funcs):
    for f in [func_dict[fname] for fname in funcs]:
        value = f(value)
    return value
