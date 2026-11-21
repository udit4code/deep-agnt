def tool_spec(name, description, properties=None, required=None):
    return {
        "name" : name,
        "description" : description,
        "input_schema" : {
            "type" : "object",
            "properties" : properties.copy() if properties is not None else {},
            "required" : required.copy() if required is not None else [],
        }
    }
