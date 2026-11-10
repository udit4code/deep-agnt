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


def tool_result(tool_use_id, content, is_error=False):
    """Return a tool_result dictionary with stringified content, adding 'is_error': True only when requested."""
    result = {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": str(content)
    }
    if is_error:
        result["is_error"] = True
    return result


def run_tool(block, registry):
    """Look up and execute a tool from the registry, handling unknown tools and exceptions."""
    # Extract tool invocation details from the block
    tool_use_id = block.get("id")
    name = block.get("name")
    inputs = block.get("input", {})
    
    # Check if the requested tool exists in the provided registry
    if name not in registry:
        return tool_result(tool_use_id, f"unknown tool '{name}'", is_error=True)
        
    try:
        # Retrieve the callable function and execute it with unpacked arguments
        fn = registry[name]
        result = fn(**inputs)
        return tool_result(tool_use_id, result)
    except Exception as e:
        # Catch any exceptions raised during execution and format them as tool errors
        error_msg = f"{type(e).__name__}: {e}"
        return tool_result(tool_use_id, error_msg, is_error=True)
