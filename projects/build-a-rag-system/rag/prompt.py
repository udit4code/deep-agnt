def numbered(chunks):
    """Lays chunks out as numbered sources for citation, separated by a blank line."""
    if not chunks:
        return ""
    
    # Enumerate starting from 1 to format each chunk as '[i] text'
    formatted_chunks = [f"[{i}] {chunk['text']}" for i, chunk in enumerate(chunks, 1)]
    
    # Join with double newlines
    return "\n\n".join(formatted_chunks)
