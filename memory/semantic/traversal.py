"""memory/semantic/traversal.py — اجتياز محكوم لشبكة العنكبوت.

الاستراتيجيات:
- BFS: Breadth-First (الأقرب أولاً)
- DFS: Depth-First (الأعمق أولاً)
- BY_WEIGHT: الأثقل خيطاً أولاً
- BY_RECENCY: الأحدث عقدة أولاً
- BY_IMPORTANCE: الأكثر ارتباطاً أولاً
"""
import sys
from pathlib import Path
from collections import deque

_here = Path(__file__).resolve().parent
_memory = _here.parent
_kernel = _memory.parent

sys.path.insert(0, str(_memory))
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_kernel / "audit"))

import gate
import graph as g
import append_only_log as audit

STRATEGIES = frozenset({
    "BFS", "DFS", "BY_WEIGHT", "BY_RECENCY", "BY_IMPORTANCE"
})


def _check_strategy(strategy):
    if strategy not in STRATEGIES:
        raise ValueError(
            f"unknown strategy '{strategy}'. "
            f"Use one of: {sorted(STRATEGIES)}"
        )


def _out_neighbors(node_id):
    """جيران خارجيون: (edge, neighbor_id)."""
    result = []
    for e in g._load_edges():
        if e["from_id"] == node_id:
            result.append((e, e["to_id"]))
    return result


def _bfs(start_id, max_depth):
    """Breadth-First: مستوى بمستوى."""
    visited = {start_id}
    order = [start_id]
    queue = deque([(start_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for _, nbr in _out_neighbors(current):
            if nbr not in visited:
                visited.add(nbr)
                order.append(nbr)
                queue.append((nbr, depth + 1))
    return order


def _dfs(start_id, max_depth):
    """Depth-First: عمق قبل العرض."""
    visited = set()
    order = []
    stack = [(start_id, 0)]
    while stack:
        current, depth = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)
        if depth >= max_depth:
            continue
        nbrs = _out_neighbors(current)
        for _, nbr in reversed(nbrs):
            if nbr not in visited:
                stack.append((nbr, depth + 1))
    return order


def _by_weight(start_id, max_depth):
    """الأثقل خيطاً أولاً."""
    visited = {start_id}
    order = [start_id]
    frontier = [(start_id, 0)]
    while frontier:
        frontier.sort(key=lambda x: -x[1])
        current, depth = frontier.pop(0)
        if depth >= max_depth:
            continue
        nbrs = _out_neighbors(current)
        nbrs.sort(key=lambda x: -x[0].get("weight", 0.0))
        for edge, nbr in nbrs:
            if nbr not in visited:
                visited.add(nbr)
                order.append(nbr)
                frontier.append((nbr, depth + 1))
    return order


def _by_recency(start_id, max_depth):
    """الأحدث عقدة أولاً."""
    visited = {start_id}
    order = [start_id]
    frontier = [(start_id, 0)]
    while frontier:
        frontier.sort(key=lambda x: x[1])
        current, depth = frontier.pop(0)
        if depth >= max_depth:
            continue
        nbrs = _out_neighbors(current)
        # نرتب حسب created_at تنازلياً
        def created_key(item):
            node = g.get_node(item[1])
            return node.get("created_at", "") if node else ""
        nbrs.sort(key=created_key, reverse=True)
        for _, nbr in nbrs:
            if nbr not in visited:
                visited.add(nbr)
                order.append(nbr)
                frontier.append((nbr, depth + 1))
    return order


def _by_importance(start_id, max_depth):
    """الأكثر ارتباطاً أولاً (درجة العقدة)."""
    visited = {start_id}
    order = [start_id]
    frontier = [(start_id, 0)]
    while frontier:
        frontier.sort(key=lambda x: x[1])
        current, depth = frontier.pop(0)
        if depth >= max_depth:
            continue
        nbrs = _out_neighbors(current)
        nbrs.sort(
            key=lambda x: -len(_out_neighbors(x[1]))
        )
        for _, nbr in nbrs:
            if nbr not in visited:
                visited.add(nbr)
                order.append(nbr)
                frontier.append((nbr, depth + 1))
    return order


def traverse(start_id, strategy="BFS", max_depth=5,
             subject=None, role=None, trust=None):
    """اجتياز الشبكة من عقدة بداية.

    يعيد قائمة node_ids بالترتيب.
    """
    _check_strategy(strategy)

    if not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError("max_depth must be non-negative int")

    # التحقق من وجود البداية
    start = g.get_node(start_id, subject=subject, role=role, trust=trust)
    if start is None:
        raise ValueError(f"start node {start_id} not found")

    # كل اجتياز يمر عبر البوابة
    gate.execute("memory:graph_traverse",
                 payload={"op": "traverse",
                          "start": start_id,
                          "strategy": strategy,
                          "max_depth": max_depth},
                 subject=subject, role=role, trust=trust)

    if strategy == "BFS":
        order = _bfs(start_id, max_depth)
    elif strategy == "DFS":
        order = _dfs(start_id, max_depth)
    elif strategy == "BY_WEIGHT":
        order = _by_weight(start_id, max_depth)
    elif strategy == "BY_RECENCY":
        order = _by_recency(start_id, max_depth)
    elif strategy == "BY_IMPORTANCE":
        order = _by_importance(start_id, max_depth)
    else:
        order = [start_id]

    audit.append("graph_traversed", {
        "start": start_id,
        "strategy": strategy,
        "max_depth": max_depth,
        "visited_count": len(order),
    })
    return order


def traverse_with_labels(start_id, strategy="BFS", max_depth=5,
                         subject=None, role=None, trust=None):
    """نفس traverse لكن يعيد (id, label) للأغراض البصرية."""
    ids = traverse(start_id, strategy, max_depth,
                   subject=subject, role=role, trust=trust)
    result = []
    for nid in ids:
        n = g.get_node(nid)
        result.append((nid, n.get("label") if n else "?"))
    return result


if __name__ == "__main__":
    import json as _json
    if len(sys.argv) > 1 and sys.argv[1] == "strategies":
        print(_json.dumps(sorted(STRATEGIES), indent=2))
    else:
        print("Usage: python -m memory.semantic.traversal strategies")
