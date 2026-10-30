import numpy as np


def cosine_similarity(query, documents):
    """Cosine similarity between a query vector and each document vector."""
    query = np.asarray(query)
    documents = np.asarray(documents)

    # Step 1 : Compute norms
    query_norm = np.linalg.norm(query)
    doc_norms = np.linalg.norm(documents, axis=1)

    # Step 2 : Compute dot products for all documents at once
    dot_products = np.dot(documents, query)

    # Compute cosine similarity with safety for zero norms
    denominator = query_norm * doc_norms
    similarities = np.divide(
        dot_products,
        denominator,
        out=np.zeros_like(dot_products, dtype=float),
        where=denominator != 0,
    )

    return similarities
