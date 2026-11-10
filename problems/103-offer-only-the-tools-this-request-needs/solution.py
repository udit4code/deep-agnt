import numpy as np


def pick_tools(request, catalog, k=5):
    """The k tools most likely to handle this message, best first."""
    if not catalog:
        return []
        
    k = min(k, len(catalog))
    
    # Construct rich descriptive text for each tool to bridge vocabulary gaps
    tool_texts = []
    for tool in catalog:
        name = tool.get("name", "")
        desc = tool.get("description", "")
        props = tool.get("input_schema", {}).get("properties", {})
        prop_desc = " ".join([f"{prop_name}: {prop_info.get('description', '')}" for prop_name, prop_info in props.items()])
        tool_texts.append(f"{name}: {desc} {prop_desc}")
        
    # Embed the request and all tool descriptions in a single model call
    texts = [request] + tool_texts
    embeddings = embedder.embed(texts)
    
    req_emb = np.array(embeddings[0])
    tool_embs = np.array(embeddings[1:])
    
    # Compute cosine similarities between the request and each tool
    dot_products = np.dot(tool_embs, req_emb)
    tool_norms = np.linalg.norm(tool_embs, axis=1)
    req_norm = np.linalg.norm(req_emb)
    
    scores = dot_products / (tool_norms * req_norm + 1e-10)
    
    # Sort indices by highest similarity score
    top_indices = np.argsort(scores)[::-1][:k]
    
    return [catalog[i] for i in top_indices]
