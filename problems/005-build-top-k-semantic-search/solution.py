import numpy as np


def cosine_similarity(query, documents):
    """Cosine similarity between a query vector and each document vector.

    Time Complexity: O(N * D)
      - N: number of documents
      - D: dimensionality of the vectors
      - Computing norms and dot products scales linearly with total elements (N * D).
    """
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


# =============================================================================
# NAIVE APPROACH: Full Sort via np.lexsort
# =============================================================================
def top_k_search_naive(query, documents, k):
    """Return the k most similar documents as [(index, score), ...], best first.

    Time Complexity: O(N * D + N log N)
      - Similarity Calculation: O(N * D)
      - Full Sorting (np.lexsort): O(N log N) because it sorts *all* N document
        scores, regardless of how small k is.
    """
    scores = cosine_similarity(query, documents)
    k = min(k, len(scores))

    # Step 1 : Create an array of original indices [0, 1, 2, ...]
    indices = np.arange(len(scores))

    # Step 2 : np.lexsort sorts ALL N scores fully.
    # Primary key: -scores (descending), Secondary key: indices (ascending for ties).
    sorted_indices = np.lexsort((indices, -scores))

    # Step 3 : Slice the top k elements
    top_indices = sorted_indices[:k]
    return [(int(idx), float(scores[idx])) for idx in top_indices]


# =============================================================================
# OPTIMIZED APPROACH: Partial Sort via np.argpartition
# =============================================================================
def top_k_search(query, documents, k):
    """Return the k most similar documents as [(index, score), ...], best first

    using an efficient partial sort.

    Time Complexity: O(N * D + N + k log k) ≈ O(N * D + k log k)
      - Similarity Calculation: O(N * D)
      - Partial Sort (np.argpartition): O(N) average time (partitions the top-k
        elements into position without fully sorting the remaining N - k items).
      - Refining Top-k Subset: O(k log k) to fully sort only the k isolated candidates.
    """
    scores = cosine_similarity(query, documents)
    n = len(scores)
    k = min(k, n)

    if k <= 0:
        return []

    # Step 1 : Partial sort using np.argpartition -> O(N) average time
    unsorted_top_k = np.argpartition(scores, -k)[-k:]

    # Step 2 : Fully sort only the top-k subset -> O(k log k) time
    # Primary key (-scores): descending; Secondary key (unsorted_top_k): lower index tie-breaker.
    sorted_indices = unsorted_top_k[
        np.lexsort((unsorted_top_k, -scores[unsorted_top_k]))
    ]

    # Step 3 : Format output as a list of native Python (index, score) tuples
    return [(int(idx), float(scores[idx])) for idx in sorted_indices]


