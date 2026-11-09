def paragraphs(text):
    return [paragraph for paragraph in (line.strip() for line in text.split("\n")) if paragraph]


def pack(paras, max_words):
    """Joins consecutive paragraphs into chunks under max_words."""
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for para in paras:
        para_words = para.split()
        para_word_count = len(para_words)
        
        # If adding this paragraph exceeds max_words, flush the current chunk first
        if current_chunk and (current_word_count + para_word_count > max_words):
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_word_count = 0
            
        current_chunk.append(para)
        current_word_count += para_word_count
        
        # If a paragraph is longer than max_words on its own, it is a chunk by itself
        if para_word_count > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_word_count = 0
            
    # Don't forget the last chunk if any paragraphs remain
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
