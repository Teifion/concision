"""
Those looking for a much fuller solution might be interested in https://github.com/andialbrecht/sqlparse/

I considered using it but wanted to writing my own to see what it'd be like.

This one will at the same time put the correct variables into the SQLAlchemy query.
"""

from sqlalchemy.sql import compiler
import re

_newlines = (
    re.compile(r" (FROM) "),
    re.compile(r" (WHERE) "),
    re.compile(r" (AND) "),
    re.compile(r" (GROUP BY) "),
    re.compile(r" (ORDER BY) "),
)

def prettify(alchemy_query, html=True):
    q_str, params = semi_compile(alchemy_query)
    
    for n in _newlines:
        q_str = n.sub("\n" + r"\1 ", q_str)
    
    return q_str % params

def semi_compile(query):
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    params = {}
    for k,v in comp.params.items():
        if isinstance(v, str):
            v = "'%s'" % v
        params[k] = v
    return comp.string, params

def compile_query(query):
    query_string, params = semi_compile(query)
    return query_string % params
