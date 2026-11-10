import inspect
import typing
import types


def tool_spec(fn):
    """Orchestrates the creation of the tool specification for a given function."""
    if not fn.__doc__:
        raise TypeError(f"Function {fn.__name__} has no docstring")
        
    # 1. Parse documentation
    doc = inspect.cleandoc(fn.__doc__)
    main_desc, arg_descs = extract_docstring_info(doc)
    
    # 2. Inspect signature and build parameters schema
    properties, required = build_parameter_properties(fn, arg_descs)
    
    return {
        "name": fn.__name__,
        "description": main_desc,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def extract_docstring_info(docstring: str):
    """Responsibility: Parse docstring text to extract the main summary and argument descriptions."""
    paragraphs = docstring.split("\n\n")
    # First paragraph's line breaks become single spaces
    main_desc = paragraphs[0].replace("\n", " ").strip()
    
    arg_descs = {}
    lines = docstring.splitlines()
    in_args = False
    current_arg = None
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Args:"):
            in_args = True
            continue
            
        if in_args:
            if not stripped:
                continue
            # If indentation drops back, we have exited the Args block
            if not line.startswith(" ") and not line.startswith("\t"):
                in_args = False
                current_arg = None
                continue
                
            if ":" in stripped:
                parts = stripped.split(":", 1)
                potential_name = parts[0].strip()
                if potential_name.isidentifier():
                    current_arg = potential_name
                    arg_descs[current_arg] = parts[1].strip()
                    continue
                    
            # Handle multi-line argument descriptions
            if current_arg is not None and (line.startswith("        ") or line.startswith("\t\t") or line.startswith("    ")):
                arg_descs[current_arg] += " " + stripped
                
    return main_desc, arg_descs


def build_parameter_properties(fn, arg_descs: dict):
    """Responsibility: Inspect function signature, resolve type hints, validate constraints, and build schema properties."""
    sig = inspect.signature(fn)
    try:
        type_hints = typing.get_type_hints(fn, include_extras=True)
    except Exception:
        type_hints = {}

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        # Validate unsupported parameter kinds (*args and **kwargs)
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise TypeError(f"Parameter '{name}' is *args or **kwargs")
        if param.annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter '{name}' has no type hint")
            
        # Resolve type hint (handling string/postponed annotations)
        resolved_type = type_hints.get(name, param.annotation)
        
        # Map Python type to JSON schema representation
        prop_schema = map_type_to_schema(resolved_type, name)
        
        # Attach argument description from docstring if available
        if name in arg_descs:
            prop_schema["description"] = arg_descs[name]
            
        properties[name] = prop_schema
        
        # Parameters without default values are required
        if param.default is inspect.Parameter.empty:
            required.append(name)
            
    return properties, required


def map_type_to_schema(t, param_name: str) -> dict:
    """Responsibility: Map an individual Python type hint into its corresponding JSON schema dictionary."""
    # Check primitive types first (Note: bool must be checked before int because bool is a subclass of int in Python)
    if t is bool:
        return {"type": "boolean"}
    if t is int:
        return {"type": "integer"}
    if t is float:
        return {"type": "number"}
    if t is str:
        return {"type": "string"}
        
    origin = typing.get_origin(t)
    args = typing.get_args(t)
    
    # Handle list / typing.List containers
    if origin in (list, typing.List):
        item_type = args[0] if args else str
        return {"type": "array", "items": map_type_to_schema(item_type, param_name)}
        
    # Handle Literal types (e.g., Literal["a", "b"] or Literal[1, 2])
    if origin is typing.Literal or str(origin) == "typing.Literal":
        if not args:
            raise TypeError(f"Parameter '{param_name}' has empty Literal")
        first_val = args[0]
        
        # Determine schema value type from the first literal choice
        if isinstance(first_val, bool):
            val_type = "boolean"
        elif isinstance(first_val, int):
            val_type = "integer"
        elif isinstance(first_val, float):
            val_type = "number"
        elif isinstance(first_val, str):
            val_type = "string"
        else:
            val_type = "string"
            
        return {"type": val_type, "enum": list(args)}
        
    # Handle Union / Optional types (e.g., Optional[X] or X | None)
    union_origins = {typing.Union}
    if hasattr(types, "UnionType"):
        union_origins.add(types.UnionType)
        
    if origin in union_origins:
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return map_type_to_schema(non_none[0], param_name)
        else:
            raise TypeError(f"Parameter '{param_name}' has unsupported union type {t}")
            
    raise TypeError(f"Parameter '{param_name}' has unsupported type {t}")
