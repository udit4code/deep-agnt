def build_tree(chunks, cluster, summarize):
    """Every node of the tree, leaves first, in id order."""
    nodes = [
        {
            "id": i,
            "level": 0,
            "text": chunk,
            "children": [],
        }
        for i, chunk in enumerate(chunks)
    ]
    next_id = len(nodes)
    layer = list(nodes)
    round_num = 0

    while len(layer) > 1:
        round_num += 1
        groups = cluster([node["text"] for node in layer])

        # Stop before any model call if clustering does not shrink the layer.
        if not groups or len(groups) >= len(layer):
            break

        next_layer = []
        for group in groups:
            if len(group) == 1:
                # Single-member group carries its existing node up unchanged.
                next_layer.append(layer[group[0]])
            else:
                members = [layer[pos] for pos in group]
                joined_texts = "\n\n".join(m["text"] for m in members)
                prompt = SUMMARY_PROMPT.format(texts=joined_texts)
                summary = summarize(prompt).strip()

                new_node = {
                    "id": next_id,
                    "level": round_num,
                    "text": summary,
                    "children": [m["id"] for m in members],
                }
                next_id += 1
                nodes.append(new_node)
                next_layer.append(new_node)

        layer = next_layer

    return sorted(nodes, key=lambda n: n["id"])


def retrieve(nodes, query, budget):
    """Ids of the best nodes at any level, best first, within `budget` tokens."""
    scored = []
    for node in nodes:
        score = similarity(query, node["text"])
        if score > 0:
            scored.append((score, node["id"], node["text"]))

    # Best score first; ties broken by lower node id first.
    scored.sort(key=lambda item: (-item[0], item[1]))

    selected_ids = []
    used_tokens = 0
    for _, node_id, text in scored:
        tokens = count_tokens(text)
        if used_tokens + tokens <= budget:
            used_tokens += tokens
            selected_ids.append(node_id)
        else:
            break

    return selected_ids
