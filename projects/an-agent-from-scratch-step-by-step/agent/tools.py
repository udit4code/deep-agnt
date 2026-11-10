def param_schema(kind, description):
    return {
        "type" : kind,
        "description" : description,
    }


def required_params(params):
    parameter_names = [ ]
    for parameter_name in params.keys():
        parameter_type, parameter_desc, is_required = params[parameter_name]
        if is_required:
            parameter_names.append(parameter_name)
    return parameter_names


def tool_spec(name, description, params):
    """Return the tool specification dictionary with properly formatted properties and schema order."""
    properties = {}
    for param_name, param_info in params.items():
        p_type = param_info[0]
        p_desc = param_info[1]
        properties[param_name] = {
            "description": p_desc,
            "type": p_type
        }
        
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required_params(params)
        }
    }
