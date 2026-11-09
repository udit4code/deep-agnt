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


def rag(system, question, k=3):
    """Answers a question using the RAG system bundle, checks for unsupported claims, and returns the full result."""
    model = system["model"]
    embedder = system["embedder"]
    index = system["index"]
    
    # 1. Get the answer and sources using answer_or_abstain
    result = answer_or_abstain(model, embedder, index, question, k=k)
    answer = result["answer"]
    sources = result["sources"]
    
    # 2. Check for unsupported sentences using unsupported()
    unsupported_sentences = unsupported(model, answer, sources)
    
    return {
        "answer": answer,
        "sources": sources,
        "unsupported": unsupported_sentences
    }
