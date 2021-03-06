from .models import ConcisionSource

"""These exist only so we don't get a compile error of any kind
ideally you would import the actual SQLAlchemy classes.
"""
class UserClass(object):
    __tablename__ = "users"

class StatTableClass(object):
    __tablename__ = "stats"

stat_table = ConcisionSource(
    db_class = StatTableClass,
    label = "Sales stats",
    keys = ("the_date", "agent"),
    
    # These are the columns we want to provide access to
    column_labels = {
        "agent": "Agent",
        "manager": "Manager",
        "the_date": "Date",
        
        "red": "Red widgets sold",
        "blue": "Blue widgets sold",
        "green": "Green widgets sold",
        "yellow": "Yellow widgets sold",
    },
    columns_from_labels = True,
    
    # Table joins
    aliases = {
        "agent": {
            "db_class": UserClass,
            "name": "agent_table",
            "table": "users",
            "column": "name",
            
            "join_on": "id",
        },
        
        "manager": {
            "db_class": UserClass,
            "name": "manager_table",
            "table": "users",
            "column": "name",
            
            "join_on": "id",
        }
    },
    
    # We're assuming all our users are stored with uppercase names
    # so this will allow us to be case-insensetive
    column_converters = {
        "agent": ["upper", "strip"],
        "manager": ["upper", "strip"],
    },
    
    # In this instances we don't want to ever show cancelled sales
    # this filter is hidden from the end user
    mandatory_filters = lambda: [StatTableClass.cancelled != None],
)
