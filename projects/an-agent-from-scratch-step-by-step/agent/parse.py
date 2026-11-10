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
