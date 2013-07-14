# I'm not sure how to separate this from the rest of my project
from ..models import Base as DeclarativeBase

from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Boolean,
    
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import (
    ARRAY,
)

import json

def build_field_getter(db_class):
    def f(key):
        if type(key) == str:
            return getattr(db_class, key)
        return key
    return f

class ConcisionSource(object):
    """
    The base object for database objects looked at by Concision
    """
    def __init__(self, db_class, **kwargs):
        super(ConcisionSource, self).__init__()
        self.db_class = db_class
        
        self.name = kwargs.get('name', db_class.__tablename__)
        self.label = kwargs.get('label', db_class.__tablename__)
        
        self.query_as_single = kwargs.get('query_as_single', True)
        self.query_as_aggregate = kwargs.get('query_as_aggregate', True)
        self.column_labels = kwargs.get('column_labels', {})
        self.column_converters = kwargs.get('column_converters', {})
        self.enums = kwargs.get('enums', {})
        
        self.mandatory_filters = kwargs.get('mandatory_filters', (lambda:()))
        
        self.allow_join = kwargs.get('allow_join', [])
        self.aliases = kwargs.get('aliases', {})
        
        if "keys" in kwargs:
            # self.keys = tuple(map(build_field_getter(db_class), kwargs['keys']))
            self.keys = kwargs['keys']
        else:
            raise Exception("Cannot auto-generate keys yet")
        
        # TODO - Document the multiple ways to pull columns
        if "columns" in kwargs:
            self.columns = kwargs['columns']
        elif "columns_from_labels" in kwargs and len(self.column_labels) > 0:
            self.columns = list(self.column_labels.keys())
            self.columns.sort()
        else:
            ignored_columns = kwargs.get('ignored_columns', [])
            self.columns = [c.name for c in db_class.__table__.columns if c not in ignored_columns]
            self.columns.sort()

class StoredQuery(DeclarativeBase):
    """Used to store a query in the database, it is then converted into
    an executable query when needed."""
    
    __tablename__ = "concision_queries"
    id       = Column(Integer, primary_key=True)
    name     = Column(String, nullable=False)
    data     = Column(Text, nullable=False)
    creator  = Column(Integer, ForeignKey("users.id"), nullable=False)
    complete = Column(Boolean, nullable=False, default=False)
    
    def extract_data(self):
        self.jdata = json.loads(self.data)
        return self.jdata
    
    def compress_data(self, d=None):
        if d == None:
            self.data = json.dumps(self.jdata)
        else:
            self.data = json.dumps(d)
        return self.data

class ConcisionReport(DeclarativeBase):
    """A report combines the data output of one or more queries in some way."""
    
    __tablename__ = "concision_reports"
    id       = Column(Integer, primary_key=True)
    name     = Column(String, nullable=False)
    creator  = Column(Integer, ForeignKey("users.id"), nullable=False)
    data     = Column(Text, nullable=False)
    
    def extract_data(self):
        self.jdata = json.loads(self.data)
        return self.jdata
    
    def compress_data(self, d=None):
        if d == None:
            self.data = json.dumps(self.jdata)
        else:
            self.data = json.dumps(d)
        return self.data
