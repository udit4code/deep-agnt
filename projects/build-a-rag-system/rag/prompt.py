def numbered(chunks):
    """Lays chunks out as numbered sources for citation, separated by a blank line."""
    if not chunks:
        return ""
    
    # Enumerate starting from 1 to format each chunk as '[i] text'
    formatted_chunks = [f"[{i}] {chunk['text']}" for i, chunk in enumerate(chunks, 1)]
    
    # Join with double newlines
    return "\n\n".join(formatted_chunks)


def fit(chunks, max_words):
    """Keeps chunks in order while their total word count stays at or under max_words, 
    with the first chunk always included.
    """
    if not chunks:
        return []
    
    kept = []
    current_word_count = 0
    
    for i, chunk in enumerate(chunks):
        word_count = len(chunk["text"].split())
        
        # The first chunk is always kept, even if it exceeds max_words alone
        if i == 0:
            kept.append(chunk)
            current_word_count += word_count
        else:
            # For subsequent chunks, only add if it stays at or under max_words
            if current_word_count + word_count <= max_words:
                kept.append(chunk)
                current_word_count += word_count
            else:
                break
                
    return kept
