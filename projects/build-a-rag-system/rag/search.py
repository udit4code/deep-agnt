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
