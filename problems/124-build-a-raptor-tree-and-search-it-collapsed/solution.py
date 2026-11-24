from dataclasses import dataclass, field


@dataclass
class TreeNode:
    """Represents a single leaf or summary node in a RAPTOR tree."""

    id: int
    level: int
    text: str
    children: list[int] = field(default_factory=list)

    @property
    def token_count(self) -> int:
        """Return token count for this node's text."""
        return count_tokens(self.text)

    def to_dict(self) -> dict:
        """Serialize the node to the expected dictionary schema."""
        return {
            "id": self.id,
            "level": self.level,
            "text": self.text,
            "children": list(self.children),
        }


@dataclass
class RaptorTree:
    """Data structure storing TreeNode objects and constructing RAPTOR layers."""

    _nodes: list[TreeNode] = field(default_factory=list)
    _next_id: int = 0

    def add_leaf(self, text: str) -> TreeNode:
        """Create and register a level-0 leaf node from a raw chunk."""
        node = TreeNode(id=self._next_id, level=0, text=text, children=[])
        self._next_id += 1
        self._nodes.append(node)
        return node

    def add_summary_node(self, members: list[TreeNode], level: int, summarize) -> TreeNode:
        """Summarize member TreeNodes into a new parent TreeNode and register it."""
        # Join member passages with a blank line to match SUMMARY_PROMPT formatting.
        joined_texts = "\n\n".join(member.text for member in members)
        prompt = SUMMARY_PROMPT.format(texts=joined_texts)
        summary_text = summarize(prompt).strip()

        node = TreeNode(
            id=self._next_id,
            level=level,
            text=summary_text,
            children=[member.id for member in members],
        )
        self._next_id += 1
        self._nodes.append(node)
        return node

    def build_next_layer(
        self,
        layer: list[TreeNode],
        level: int,
        cluster,
        summarize,
    ) -> list[TreeNode] | None:
        """Cluster one TreeNode layer into the next, or return None if no progress."""
        groups = cluster([node.text for node in layer])

        # Stop before any model call if clustering does not shrink the layer.
        if not groups or len(groups) >= len(layer):
            return None

        next_layer = []
        for group in groups:
            if len(group) == 1:
                # Promote a singleton node unchanged to avoid redundant summaries.
                next_layer.append(layer[group[0]])
            else:
                members = [layer[pos] for pos in group]
                summary_node = self.add_summary_node(
                    members=members,
                    level=level,
                    summarize=summarize,
                )
                next_layer.append(summary_node)

        return next_layer

    def sorted_nodes(self, as_dicts: bool = True) -> list[dict | TreeNode]:
        """Return all nodes ordered by ascending id."""
        ordered = sorted(self._nodes, key=lambda node: node.id)
        return [node.to_dict() for node in ordered] if as_dicts else ordered


def _node_fields(node: dict | TreeNode) -> tuple[int, str, int]:
    """Extract (id, text, token_count) from either a dict or TreeNode."""
    if isinstance(node, TreeNode):
        return node.id, node.text, node.token_count
    return node["id"], node["text"], count_tokens(node["text"])


def build_tree(chunks, cluster, summarize):
    """Build a RAPTOR tree over chunks and return all nodes in id order."""
    tree = RaptorTree()

    # Step 1: Create level-0 leaf TreeNodes in chunk order.
    current_layer = [tree.add_leaf(chunk) for chunk in chunks]

    # Step 2: Iteratively build higher layers until a single root or stall.
    round_num = 0
    while len(current_layer) > 1:
        round_num += 1
        next_layer = tree.build_next_layer(
            layer=current_layer,
            level=round_num,
            cluster=cluster,
            summarize=summarize,
        )
        if next_layer is None:
            break
        current_layer = next_layer

    # Return sorted node dicts from the tree data structure.
    return tree.sorted_nodes(as_dicts=True)


def _rank_candidates(nodes: list[dict | TreeNode], query: str) -> list[tuple[float, int, int]]:
    """Score non-zero matches; return (similarity, node_id, token_count) sorted."""
    ranked = []
    for node in nodes:
        node_id, text, tokens = _node_fields(node)
        score = similarity(query, text)
        if score > 0:
            ranked.append((score, node_id, tokens))

    # Highest similarity first; ties broken by smallest node id.
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked


def retrieve(nodes, query, budget):
    """Return ids of top-scoring nodes within `budget` tokens, best first."""
    ranked = _rank_candidates(nodes, query)

    selected_ids = []
    tokens_used = 0
    for _, node_id, node_tokens in ranked:
        # Stop at the first node that exceeds the remaining token budget.
        if tokens_used + node_tokens > budget:
            break
        tokens_used += node_tokens
        selected_ids.append(node_id)

    return selected_ids
