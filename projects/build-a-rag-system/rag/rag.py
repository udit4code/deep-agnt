def build_rag(model, embedder, docs, max_words=80):
    """Chunks the documents, builds the index in one embedding call, and returns the RAG suite bundle."""
    # Chunk the documents using the specified max_words budget
    chunks = chunk_docs(docs, max_words=max_words)
    
    # Build the index (which embeds the chunks in one call via embed_texts)
    index = build_index(embedder, chunks)
    
    return {
        "model": model,
        "embedder": embedder,
        "index": index
    }
