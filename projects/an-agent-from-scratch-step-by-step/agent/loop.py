def user_message(text):
    """Return a user role message dictionary with the given text content."""
    return {"role": "user", "content": text}


def results_message(results):
    """Return a user message whose content is the list of tool_result blocks."""
    return {"role": "user", "content": results}
