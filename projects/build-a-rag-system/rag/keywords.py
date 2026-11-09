import re

def words(text):
    """Returns the words of text as a list, lowercased: runs of letters and digits, nothing else."""
    return re.findall(r'[a-zA-Z0-9]+', text.lower())


def keyword_rank(chunks, question):
    """Returns the chunks' ids ordered by how many distinct words of the question appear in the chunk."""
    if not chunks:
        return []
    
    # Get distinct words from the question using the provided words() function
    q_words = set(words(question))
    
    scored_chunks = []
    for idx, chunk in enumerate(chunks):
        # Get distinct words from the chunk text
        chunk_words = set(words(chunk["text"]))
        # Count distinct words of the question present in the chunk
        match_count = len(q_words.intersection(chunk_words))
        scored_chunks.append((match_count, idx, chunk["id"]))
    
    # Sort by match_count descending. 
    # For ties, -x[1] (ascending original index) with reverse=True ensures earlier chunks come first.
    sorted_chunks = sorted(scored_chunks, key=lambda x: (x[0], -x[1]), reverse=True)
    
    return [chunk_id for _, _, chunk_id in sorted_chunks]


from collections import defaultdict

def rrf(rankings, k=60):
    """Fuses several rankings (lists of ids) using Reciprocal Rank Fusion."""
    scores = defaultdict(float)
    first_seen = {}
    order_counter = 0
    
    # Accumulate scores and track the order of first appearance across rankings
    for ranking in rankings:
        for i, item in enumerate(ranking):
            scores[item] += 1.0 / (k + i + 1)
            if item not in first_seen:
                first_seen[item] = order_counter
                order_counter += 1
                
    # Sort items by score descending. 
    # For ties, -first_seen[x] ensures that items seen earlier (smaller first_seen index) come first.
    sorted_items = sorted(
        scores.keys(),
        key=lambda x: (scores[x], -first_seen[x]),
        reverse=True
    )
    
    return sorted_items
