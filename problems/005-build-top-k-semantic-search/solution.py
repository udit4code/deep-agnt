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


# NAIVE APPROACH : 
def top_k_search_naive(query, documents, k):
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



def top_k_search(query, documents, k):
    """Return the k most similar documents as [(index, score), ...], best first

    using an efficient partial sort.
    """
    scores = cosine_similarity(query, documents)
    n = len(scores)
    k = min(k, n)

    if k <= 0:
        return []

    # 1. Partial sort using np.argpartition (O(N) average time)
    unsorted_top_k = np.argpartition(scores, -k)[-k:]

    # 2. Fully sort the top-k subset using np.lexsort
    # Note: np.lexsort takes keys as (secondary_key, primary_key).
    # - Primary key (-scores[unsorted_top_k]): Sorts scores in descending order.
    # - Secondary key (unsorted_top_k): Breaks ties by picking the lower index first.
    sorted_indices = unsorted_top_k[
        np.lexsort((unsorted_top_k, -scores[unsorted_top_k]))
    ]

    # 3. Format output as a list of native Python (index, score) tuples
    return [(int(idx), float(scores[idx])) for idx in sorted_indices]


