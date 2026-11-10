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
