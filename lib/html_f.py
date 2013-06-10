from collections import OrderedDict, defaultdict

def _sort_elements(sequence, element_property="name", reverse=False, as_list=False):
    """Sorts the elements of a dictionary or list while preserving their numerical order"""
    new_sequence = OrderedDict()
    
    if type(sequence) == set:
        sequence = list(sequence)
    
    if type(sequence) in (list, tuple, filter, map):
        true_sequence = list(sequence)
        ordered_sequence = list(sequence)
        ordered_sequence.sort()
        
        for i in ordered_sequence:
            new_sequence[true_sequence.index(i)] = i
    
    elif type(sequence) in (dict, OrderedDict, defaultdict):
        try:
            reverse_dict = {v:k for k, v in sequence.items()}
            ordered_sequence = [v for k, v in sequence.items()]
            ordered_sequence.sort()

            for i in ordered_sequence:
                new_sequence[reverse_dict[i]] = i
        
        except TypeError as e:
            # We need to use the element_property
            reverse_dict = {v.__dict__[element_property]:k for k, v in sequence.items()}
            ordered_sequence = [v.__dict__[element_property] for k, v in sequence.items()]
            ordered_sequence.sort()
        
            for i in ordered_sequence:
                new_sequence[reverse_dict[i]] = i
        
        except Exception as e:
            raise
        
    else:
        raise Exception("Cannot sort type: %s" % type(sequence))
    
    # Flip it about!
    if reverse:
        r = OrderedDict()
        keys = list(new_sequence.keys())
        keys.reverse()
        for k in keys:
            r[k] = new_sequence[k]
        
        new_sequence = r
    
    # As a list?
    if as_list:
        new_sequence = [v for k,v in new_sequence.items()]
    
    return new_sequence

def option_box(name, elements, selected="", tab_index = -1, custom_id="<>", onchange="", style="", disabled=[], insert_dud=False, element_property="name", css_class="", sort=True):
    disabled_count = 0
    
    output = ['<select name="{name}" style="{style}" {custom_id}onchange="{onchange}" class="{css_class}"'.format(
        name = name,
        custom_id = 'id="%s" ' % (custom_id if custom_id != "<>" else name),
        onchange = onchange,
        style = style,
        css_class = css_class,
    )]
    
    if tab_index > 0:
        output.append('tabIndex="{}"'.format(tab_index))
    
    output.append('>')
    
    if insert_dud != False:
        if type(insert_dud) == tuple or type(insert_dud) == list:
            output.append('<option value="{1}">{0}</option>'.format(*insert_dud))
        else:
            output.append('<option value="">{}</option>'.format(insert_dud))
    
    # Sort?
    if sort:
        elements = _sort_elements(elements, element_property)
    
    # Is it a list/tuple or dictionary
    if type(elements) in (list, tuple):
        iterator = enumerate(elements)
    else:
        iterator = elements.items()
    
    for k, v in iterator:
        if type(v) == tuple and len(v) == 2:
            k, v = v
        
        if type(v) not in (str, int):
            v = v.__dict__[element_property]
        
        is_selected = ""
        try:
            if int(selected) == int(k):
                is_selected = 'selected="selected"'
        except Exception:
            if selected == k:
                is_selected = 'selected="selected"'
        
        if k in disabled:
            disabled_count += 1
            output.append('<option value="disabled_{}" disabled="disabled">&nbsp;</option>'.format(disabled_count))
            continue
        
        output.append('<option value="{}" {}>{}</option>'.format(k, is_selected, v))
    
    output.append('</select>')
    return "".join(output)

def dumps(the_obj):
    data = []
    data.append(str(dir(the_obj)))
    for d in dir(the_obj):
        data.append("%s: %s" % (d, getattr(the_obj, d)))
    return data
