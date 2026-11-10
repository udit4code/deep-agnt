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
