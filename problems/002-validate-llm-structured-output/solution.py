import json
import re


def parse_model_json(reply):
    """Return the JSON object in a model's reply, or None if there isn't one."""
    if isinstance(reply, dict):
        return reply
    if not isinstance(reply, str):
        return None

    cleaned = re.sub(
        r"^```(?:json)?|```$", "", reply.strip(), flags=re.IGNORECASE
    ).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and start < end:
        candidate = cleaned[start : end + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def validate_response(raw, schema):
    """Parse and validate a model's JSON reply against a {field: type} schema.

    Return the cleaned dict, or None if it cannot be trusted.
    """
    if not isinstance(schema, dict):
        return None

    # Step 1 : Parse and extract the JSON object safely
    parsed = parse_model_json(raw)
    if parsed is None:
        return None

    # Step 2 : Validate all required schema fields and their types
    cleaned = {}
    for field, expected_type in schema.items():
        if field not in parsed:
            return None  # Missing required field

        val = parsed[field]

        # Step 2.1 : Python quirk: isinstance(True, int) is True.
        # Explicitly prevent booleans from passing as integers or floats.
        if expected_type in (int, float) and type(val) is bool:
            return None

        if not isinstance(val, expected_type):
            return None

        cleaned[field] = val

    return cleaned
