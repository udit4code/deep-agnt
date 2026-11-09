from agentkit import ToolError

def checked_call(registry, name, arguments, schema):
    """Validate arguments against the schema, then call. Returns (ok, value)."""
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # 1. Check that every required field is present
    for req in required:
        if req not in arguments:
            return (False, f"argument '{req}' is required")

    # 2. Check that no undeclared keys appear
    for key in arguments:
        if key not in properties:
            return (False, f"unknown argument '{key}'")

    # 3. Type checking
    type_map = {
        "string": str,
        "boolean": bool,
        "number": (int, float)
    }

    for field, value in arguments.items():
        prop_schema = properties.get(field, {})
        expected_type_str = prop_schema.get("type")

        if expected_type_str in type_map:
            if expected_type_str == "number":
                # bool is a subclass of int in Python, so exclude bool explicitly
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return (False, f"argument '{field}' must be number")
            elif expected_type_str == "boolean":
                if not isinstance(value, bool):
                    return (False, f"argument '{field}' must be boolean")
            elif expected_type_str == "string":
                if not isinstance(value, str):
                    return (False, f"argument '{field}' must be string")

    # 4. Execute the call if validation passes
    try:
        result = registry.call(name, arguments)
        return (True, result)
    except ToolError as e:
        return (False, str(e))
    except Exception as e:
        return (False, str(e))
