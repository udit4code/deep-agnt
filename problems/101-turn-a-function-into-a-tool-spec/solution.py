import inspect
import typing
import types


def tool_spec(fn):
    """The spec a model reads for `fn`: name, description, input_schema."""
    if not fn.__doc__:
        raise TypeError(f"Function {fn.__name__} has no docstring")
        
    doc = inspect.cleandoc(fn.__doc__)
    paragraphs = doc.split("\n\n")
    description = paragraphs[0].replace("\n", " ").strip()
    
    # Parse Args block for parameter descriptions
    arg_descs = {}
    lines = doc.splitlines()
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
            if current_arg is not None and (line.startswith("        ") or line.startswith("\t\t") or line.startswith("    ")):
                arg_descs[current_arg] += " " + stripped

    sig = inspect.signature(fn)
    try:
        type_hints = typing.get_type_hints(fn, include_extras=True)
    except Exception:
        type_hints = {}

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            raise TypeError(f"Parameter '{name}' is *args or **kwargs")
        if param.annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter '{name}' has no type hint")
            
        resolved_type = type_hints.get(name, param.annotation)
        
        prop_schema = parse_type(resolved_type, name)
        if name in arg_descs:
            prop_schema["description"] = arg_descs[name]
            
        properties[name] = prop_schema
        
        if param.default is inspect.Parameter.empty:
            required.append(name)
            
    return {
        "name": fn.__name__,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def parse_type(t, param_name):
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
    
    if origin in (list, typing.List):
        item_type = args[0] if args else str
        return {"type": "array", "items": parse_type(item_type, param_name)}
        
    if origin is typing.Literal or str(origin) == "typing.Literal":
        if not args:
            raise TypeError(f"Parameter '{param_name}' has empty Literal")
        first_val = args[0]
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
        
    union_origins = {typing.Union}
    if hasattr(types, "UnionType"):
        union_origins.add(types.UnionType)
        
    if origin in union_origins:
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return parse_type(non_none[0], param_name)
        else:
            raise TypeError(f"Parameter '{param_name}' has unsupported union type {t}")
            
    raise TypeError(f"Parameter '{param_name}' has unsupported type {t}")
