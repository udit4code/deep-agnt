def text_blocks(response):
    """Return the text of every block whose type is 'text', in order."""
    # Safely handle missing or empty content
    content_list = response.get("content")
    if not content_list:
      return []

    text_blocks_list = []
    for block in content_list:
      if isinstance(block, dict) and block.get("type") == "text":
        text_blocks_list.append(block.get("text", ""))
        
    return text_blocks_list


def text_of(response):
    """Extract text blocks, join them with a newline, and strip the result."""
    blocks = text_blocks(response)
    if not blocks:
        return ""
    return "\n".join(blocks).strip()


def tool_uses(response):
    """Return the blocks whose type is 'tool_use', in order, unchanged."""
    content_list = response.get("content")
    if not content_list:
        return []
    tool_uses_list = []
    for block in content_list:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tool_uses_list.append(block)
    return tool_uses_list


def wants_tool(response):
    """Return True when stop_reason is 'tool_use' and False otherwise."""
    if not isinstance(response, dict):
        return False
    return response.get("stop_reason") == "tool_use"


def assistant_message(response):
    """Return an assistant role message with the response's content, defaulting to [] if empty."""
    if not isinstance(response, dict):
        return {"role": "assistant", "content": []}
        
    content = response.get("content")
    if content is None:
        content = []
        
    return {"role": "assistant", "content": content}
