import difflib


def tree_diff(before, after):
    """The fewest ops that turn `before` into `after`, moves recognised."""
    # Step 1. Identify modified paths (exist in both with different content)
    modifies = []
    for p in before:
        if p in after and before[p] != after[p]:
            modifies.append({"op": "modify", "path": p, "content": after[p]})
            
    # Vanished paths and new paths
    v_paths = [p for p in before if p not in after]
    n_paths = [q for q in after if q not in before]
    
    paired_new = set()
    renames = []
    
    # Process vanished paths in sorted order for deterministic pairing
    for p in sorted(v_paths):
        content = before[p]
        candidates = [q for q in n_paths if q not in paired_new and after[q] == content]
        if candidates:
            # Pair with closest path (highest difflib ratio), tie-breaking by smaller new path
            best_q = min(candidates, key=lambda q: (-difflib.SequenceMatcher(None, p, q).ratio(), q))
            paired_new.add(best_q)
            renames.append({"op": "rename", "from": p, "to": best_q})
            
    deletes = [{"op": "delete", "path": p} for p in v_paths if not any(r["from"] == p for r in renames)]
    adds = [{"op": "add", "path": q, "content": after[q]} for q in n_paths if q not in paired_new]
    
    # Sort groups according to specifications
    renames.sort(key=lambda x: x["from"])
    modifies.sort(key=lambda x: x["path"])
    adds.sort(key=lambda x: x["path"])
    deletes.sort(key=lambda x: x["path"])
    
    return renames + modifies + adds + deletes


def apply_ops(before, ops):
    """`before` with the ops applied in order."""
    tree = dict(before)
    for op in ops:
        t = op["op"]
        if t == "rename":
            p = op["from"]
            q = op["to"]
            if p in tree:
                tree[q] = tree.pop(p)
        elif t == "modify":
            p = op["path"]
            tree[p] = op["content"]
        elif t == "add":
            p = op["path"]
            tree[p] = op["content"]
        elif t == "delete":
            p = op["path"]
            if p in tree:
                tree.pop(p)
    return tree
