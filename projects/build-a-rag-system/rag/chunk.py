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


def chunk_docs(docs, max_words=80):
    """Returns one list of chunks across every document in the order of docs."""
    all_chunks = []
    
    for doc_id, text in docs.items():
        # Split text into non-empty paragraphs
        paras = [paragraph for paragraph in text.split("\n") if paragraph.strip()]
        
        # Pack paragraphs into chunks using the pack function
        chunk_texts = pack(paras, max_words)
        
        # Build chunk dictionaries with formatted IDs
        for chunk_id, chunk_text in enumerate(chunk_texts):
            all_chunks.append({
                "id": f"{doc_id}:{chunk_id}",
                "doc": doc_id,
                "text": chunk_text
            })
            
    return all_chunks
