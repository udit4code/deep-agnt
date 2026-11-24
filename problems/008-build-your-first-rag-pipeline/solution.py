def answer(question, documents, model, k=3):
    """Chunk, retrieve, build context, and ask the model."""
    # STEP 1: Chunk every document into passages with chunk_size=40 and overlap=10,
    # keeping track of each chunk's source document index for provenance.
    passage_chunks = []
    for doc_id, document in enumerate(documents):
        chunks = chunk_document(document, 40, 10)
        for chunk in chunks:
            passage_chunks.append({
                "doc_id": doc_id,
                "chunk": chunk,
            })

    # Handle the edge case where no chunks are produced.
    if not passage_chunks:
        prompt = f"Context:\n\nQuestion: {question}"
        return model.ask(prompt)

    # STEP 2: Extract chunk strings and embed all chunks plus the question in one batch.
    chunk_texts = [item["chunk"] for item in passage_chunks]
    chunk_vectors = embed(chunk_texts)       # Shape: (num_chunks, 64), normalized
    question_vector = embed([question])[0]   # Shape: (64,), normalized

    # STEP 3: Compute cosine similarity via dot product and rank indices highest-first.
    scores = chunk_vectors @ question_vector
    top_k = min(k, len(passage_chunks))
    ranked_indices = sorted(
        range(len(passage_chunks)),
        key=lambda idx: scores[idx],
        reverse=True,
    )[:top_k]

    # STEP 4: Build the context block by joining the top-k chunks with a blank line.
    top_chunks = [passage_chunks[idx]["chunk"] for idx in ranked_indices]
    context = "\n\n".join(top_chunks)

    # STEP 5: Format the prompt with both context and question, then return model output.
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    return model.ask(prompt)

