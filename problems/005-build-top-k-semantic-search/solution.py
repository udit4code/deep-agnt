import numpy as np


def cosine_similarity(query, documents):
    """Cosine similarity between a query vector and each document vector."""
    query = np.asarray(query)
    documents = np.asarray(documents)

    query_norm = np.linalg.norm(query)
    doc_norms = np.linalg.norm(documents, axis=1)
    dot_products = np.dot(documents, query)

    denominator = query_norm * doc_norms
    similarities = np.divide(
        dot_products,
        denominator,
        out=np.zeros_like(dot_products, dtype=float),
        where=denominator != 0,
    )
    return similarities


def top_k_search(query, documents, k):
    """Return the k most similar documents as [(index, score), ...], best first."""
    scores = cosine_similarity(query, documents)
    k = min(k, len(scores))

    # Step 1 : Create an array of original indices [0, 1, 2, ...]
    indices = np.arange(len(scores))

    # Step 2 : np.lexsort sorts by multiple keys:
    # 1. Primary key (last in tuple): -scores (sorts highest score first / descending)
    # 2. Secondary key (penultimate): indices (breaks ties by picking lower index first)
    sorted_indices = np.lexsort((indices, -scores))

    top_indices = sorted_indices[:k]
    return [(int(idx), float(scores[idx])) for idx in top_indices]

