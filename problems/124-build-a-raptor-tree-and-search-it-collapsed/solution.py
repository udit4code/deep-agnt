from dataclasses import dataclass, field


@dataclass
class RaptorTree:
    """Data structure storing RAPTOR tree nodes across all levels."""

    nodes: list[dict] = field(default_factory=list)
    _next_id: int = 0

    def add_leaf(self, text: str) -> dict:
        """Create and register a level-0 leaf node from a raw text chunk."""
        node = {
            "id": self._next_id,
            "level": 0,
            "text": text,
            "children": [],
        }
        self._next_id += 1
        self.nodes.append(node)
        return node

    def add_summary_node(self, members: list[dict], level: int, summarize) -> dict:
        """Summarize member nodes into a new parent node and register it."""
        # Join member passages with a blank line as expected by SUMMARY_PROMPT.
        joined_texts = "\n\n".join(member["text"] for member in members)
        prompt = SUMMARY_PROMPT.format(texts=joined_texts)
        summary_text = summarize(prompt).strip()

        node = {
            "id": self._next_id,
            "level": level,
            "text": summary_text,
            "children": [member["id"] for member in members],
        }
        self._next_id += 1
        self.nodes.append(node)
        return node

    def sorted_nodes(self) -> list[dict]:
        """Return all tree nodes ordered by ascending node id."""
        return sorted(self.nodes, key=lambda node: node["id"])


def _build_next_layer(
    tree: RaptorTree,
    layer: list[dict],
    level: int,
    cluster,
    summarize,
) -> list[dict] | None:
    """Cluster one layer into the next layer, or return None if no progress is made."""
    groups = cluster([node["text"] for node in layer])

    # Guard against infinite loops when clustering does not reduce the layer size.
    if not groups or len(groups) >= len(layer):
        return None

    next_layer = []
    for group in groups:
        if len(group) == 1:
            # Promote a singleton node unchanged to avoid redundant summaries.
            next_layer.append(layer[group[0]])
        else:
            members = [layer[pos] for pos in group]
            summary_node = tree.add_summary_node(members=members, level=level, summarize=summarize)
            next_layer.append(summary_node)

    return next_layer


def build_tree(chunks, cluster, summarize):
    """Build a RAPTOR tree over chunks and return all nodes in id order."""
    tree = RaptorTree()

    # Step 1: Populate leaf nodes (level 0) in chunk order.
    current_layer = [tree.add_leaf(chunk) for chunk in chunks]

    # Step 2: Iteratively cluster and summarize layers until a single root or stall.
    round_num = 0
    while len(current_layer) > 1:
        round_num += 1
        next_layer = _build_next_layer(
            tree=tree,
            layer=current_layer,
            level=round_num,
            cluster=cluster,
            summarize=summarize,
        )
        if next_layer is None:
            break
        current_layer = next_layer

    # Return sorted nodes from the tree data structure.
    return tree.sorted_nodes()


def _rank_candidates(nodes: list[dict], query: str) -> list[tuple[float, int, str]]:
    """Score non-zero matches across all levels; sort by score desc, then id asc."""
    ranked = []
    for node in nodes:
        score = similarity(query, node["text"])
        if score > 0:
            ranked.append((score, node["id"], node["text"]))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked


def retrieve(nodes, query, budget):
    """Return ids of top-scoring nodes within `budget` tokens, best first."""
    ranked = _rank_candidates(nodes, query)

    selected_ids = []
    tokens_used = 0
    for _, node_id, text in ranked:
        node_tokens = count_tokens(text)
        # Stop at the first node that exceeds the remaining token budget.
        if tokens_used + node_tokens > budget:
            break
        tokens_used += node_tokens
        selected_ids.append(node_id)

    return selected_ids
