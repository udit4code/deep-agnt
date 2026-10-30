import json
import re


def parse_model_json(reply):
    """Return the JSON object in a model's reply, or None if there isn't one."""
    if not isinstance(reply, str):
        return None

    # Step 1 : Strip standard markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?|```$", "", reply.strip(), flags=re.IGNORECASE).strip()

    # Step 2 : Find the outermost JSON object bounds: first '{' to last '}'
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
