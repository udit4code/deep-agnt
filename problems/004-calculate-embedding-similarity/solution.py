import numpy as np


def cosine_similarity(query, documents):
    """Cosine similarity between a query vector and each document vector."""
    query = np.asarray(query)
    documents = np.asarray(documents)

    # Step 1 : Compute norms
    query_norm = np.linalg.norm(query)  # Shape: () [scalar]
    doc_norms = np.linalg.norm(documents, axis=1)  # Shape: (N,) [one norm per doc]

    # Step 2 : Compute dot products for all documents at once
    dot_products = np.dot(
        documents, query
    )  # Shape: (N,) [matrix (N, D) dot vector (D,)]

    # Step 3 : Compute denominator (BROADCASTING USED HERE)
    # query_norm is a scalar (), doc_norms is a 1D array (N,).
    # NumPy broadcasts the scalar across the 1D array elements.
    denominator = query_norm * doc_norms  # Shape: () * (N,) -> broadcasts to (N,)

    # Step 4 : Division and zero-safety check (BROADCASTING USED HERE)
    # denominator != 0 compares a (N,) array with a scalar 0 (scalar broadcasts to (N,)).
    similarities = np.divide(
        dot_products,
        denominator,
        out=np.zeros_like(dot_products, dtype=float),
        where=denominator != 0,
    )  # Shape: (N,) / (N,) -> (N,)

    return similarities
