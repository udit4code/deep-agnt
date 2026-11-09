import numpy as np 

def cosine(a, b):
    """Calculate the cosine similarity between two vectors a and b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    
    # Prevent division by zero if either vector is a zero vector
    if a_norm == 0.0 or b_norm == 0.0:
        return 0.0 
        
    dot_product = np.dot(a, b)
    cosine_product = dot_product / (a_norm * b_norm)
    
    # Return as a standard Python float
    return float(cosine_product)


def embed_texts(embedder, texts):
    """Returns the vectors for texts, in order, from one call to embedder.embed(texts)."""
    if not texts:
        return []
    return embedder.embed(texts)


def build_index(embedder, chunks):
    """Embeds every chunk's text in one call and returns a list of indexed chunk dictionaries."""
    if not chunks:
        return []
    
    # Extract all texts from the chunks
    texts = [chunk["text"] for chunk in chunks]
    
    # Embed all texts in a single batch call using embed_texts
    vectors = embed_texts(embedder, texts)
    
    # Combine chunks and their corresponding vectors in order
    return [{"chunk": chunk, "vector": vector} for chunk, vector in zip(chunks, vectors)]


import heapq

def nearest(index, vector, k=3):
    """Returns the top k chunks most similar to vector by cosine in O(N log k) time."""
    if not index:
        return []
    
    # heapq.nlargest finds the top k efficiently.
    # Tuple key: (cosine_similarity, -original_index) ensures stable tie-breaking 
    # (higher similarity first, and for ties, the earlier index comes first).
    top_entries = heapq.nlargest(
        k,
        enumerate(index),
        key=lambda item: (cosine(item[1]["vector"], vector), -item[0])
    )
    
    return [entry["chunk"] for _, entry in top_entries]


def search(embedder, index, question, k=3):
    """Embeds the question in one call and returns the k nearest chunks."""
    if not index or not question:
        return []
    
    # Embed the question as a single-item list (one call)
    vectors = embed_texts(embedder, [question])
    if not vectors:
        return []
    
    query_vector = vectors[0]
    
    # Find and return the k nearest chunks using nearest
    return nearest(index, query_vector, k=k)
