def _embed(inputs):
    """Helper to call embedder safely whether it is callable or uses a method."""
    if callable(embedder):
        return embedder(inputs)
    elif hasattr(embedder, "embed"):
        return embedder.embed(inputs)
    elif hasattr(embedder, "encode"):
        return embedder.encode(inputs)
    raise AttributeError("Embedder instance has no recognized embed method.")

def build_index(docs):
    """Embed every article once in a single batch call. Return an index that keeps each id with its vector."""
    texts = [doc["text"] for doc in docs]
    vectors = _embed(texts)
    return [{"id": doc["id"], "vector": vector} for doc, vector in zip(docs, vectors)]


def search(index, query, k=3):
    """The ids of the k articles nearest the query, nearest first."""
    # Embed the query (wrapped in a list to match batch input expectation)
    query_res = _embed([query])
    query_vector = query_res[0] if isinstance(query_res, list) and len(query_res) > 0 else query_res
    
    # Compute cosine similarity between the query and each indexed document vector
    scored = []
    for item in index:
        sim = cosine(query_vector, item["vector"])
        scored.append((sim, item["id"]))
        
    # Sort descending by similarity score, with alphabetical tie-breaking on ID
    scored.sort(key=lambda x: (-x[0], x[1]))
    
    return [doc_id for _, doc_id in scored[:k]]
