
def tablist(data):
    tablist = set(["queries"])
    
    # if len(data.get('tables', [])) > 0:
    #     tablist.add('columns')
    #     tablist.add('filters')
    
    # if len(data.get('columns', [])) > 0:
    #     tablist.add('execute')
    #     tablist.add('groupby')
    #     tablist.add('orderby')
    #     tablist.add('graphing')
    
    # if data.get('key', None) is not None:
    #     tablist.add('view_graph')
    
    return tablist
