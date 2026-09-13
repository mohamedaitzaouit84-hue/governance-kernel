"""memory/semantic/graph.py — شبكة العنكبوت الدلالية.

- add_node(label, properties) -> node_id
- add_edge(from_id, to_id, weight) -> edge_id
- get_node(node_id) -> Node
- get_edge(edge_id) -> Edge
- neighbors(node_id) -> list of (edge, neighbor_id)
- stats() -> dict

الحدود: MAX_NODES=100, MAX_EDGES=500 (من FREEZE_v0.2).
"""
import json
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

_here = Path(__file__).resolve().parent
_memory = _here.parent
_kernel = _memory.parent

sys.path.insert(0, str(_memory))
sys.path.insert(0, str(_memory / "episodic"))
sys.path.insert(0, str(_kernel / "audit"))

import gate
import event_log
import append_only_log as audit
from node import Node
from edge import Edge

KERNEL_DIR = _kernel
DATA_DIR = KERNEL_DIR / "memory" / "data"
NODES_PATH = DATA_DIR / "nodes.jsonl"
EDGES_PATH = DATA_DIR / "edges.jsonl"
MAX_NODES = 100
MAX_EDGES = 500

_NODES = None
_EDGES = None


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load_nodes():
    global _NODES
    if _NODES is not None:
        return _NODES
    _NODES = []
    if not NODES_PATH.exists():
        return _NODES
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    _NODES.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return _NODES


def _load_edges():
    global _EDGES
    if _EDGES is not None:
        return _EDGES
    _EDGES = []
    if not EDGES_PATH.exists():
        return _EDGES
    with open(EDGES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    _EDGES.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return _EDGES


def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path, record):
    _ensure_dirs()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False,
                           separators=(",", ":")) + "\n")


def add_node(label, properties=None, subject=None, role=None, trust=None):
    """إضافة عقدة جديدة."""
    if not isinstance(label, str) or not label:
        raise ValueError("label must be non-empty string")
    props = properties or {}

    gate.execute("memory:write",
                 payload={"op": "add_node", "label": label},
                 subject=subject, role=role, trust=trust)

    nodes = _load_nodes()
    if len(nodes) >= MAX_NODES:
        raise RuntimeError(
            f"MAX_NODES={MAX_NODES} reached. Cannot add node."
        )

    node_id = "nd_" + uuid.uuid4().hex[:16]
    n = Node(node_id=node_id, label=label,
             properties=props, created_at=_now())
    record = n.to_dict()
    record["hash"] = n.compute_hash()

    nodes.append(record)
    _append_jsonl(NODES_PATH, record)

    event_log.append("node_added",
                     {"node_id": node_id, "label": label},
                     {"op": "add_node"})
    return node_id


def add_edge(from_id, to_id, relation="related", weight=1.0,
             properties=None, subject=None, role=None, trust=None):
    """إضافة خيط يربط عقدتين."""
    if not (isinstance(weight, (int, float)) and 0 <= weight <= 1):
        raise ValueError("weight must be in [0, 1]")
    props = properties or {}

    gate.execute("memory:write",
                 payload={"op": "add_edge",
                          "from": from_id, "to": to_id},
                 subject=subject, role=role, trust=trust)

    edges = _load_edges()
    if len(edges) >= MAX_EDGES:
        raise RuntimeError(
            f"MAX_EDGES={MAX_EDGES} reached. Cannot add edge."
        )

    # التحقق من وجود العقد
    nodes = _load_nodes()
    node_ids = {n["node_id"] for n in nodes}
    if from_id not in node_ids:
        raise ValueError(f"from_id {from_id} not found")
    if to_id not in node_ids:
        raise ValueError(f"to_id {to_id} not found")

    edge_id = "ed_" + uuid.uuid4().hex[:16]
    e = Edge(edge_id=edge_id, from_id=from_id, to_id=to_id,
             relation=relation, weight=float(weight),
             properties=props, created_at=_now())
    record = e.to_dict()
    record["hash"] = e.compute_hash()

    edges.append(record)
    _append_jsonl(EDGES_PATH, record)

    event_log.append("edge_added",
                     {"edge_id": edge_id,
                      "from": from_id, "to": to_id,
                      "weight": float(weight)},
                     {"op": "add_edge"})
    return edge_id


def get_node(node_id, subject=None, role=None, trust=None):
    """استرجاع عقدة."""
    gate.execute("memory:read",
                 payload={"op": "get_node", "id": node_id},
                 subject=subject, role=role, trust=trust)
    for n in _load_nodes():
        if n["node_id"] == node_id:
            return n
    return None


def get_edge(edge_id, subject=None, role=None, trust=None):
    """استرجاع خيط."""
    gate.execute("memory:read",
                 payload={"op": "get_edge", "id": edge_id},
                 subject=subject, role=role, trust=trust)
    for e in _load_edges():
        if e["edge_id"] == edge_id:
            return e
    return None


def neighbors(node_id, direction="out",
              subject=None, role=None, trust=None):
    """جيران عقدة (عبر الخيوط)."""
    gate.execute("memory:graph_traverse",
                 payload={"op": "neighbors", "start": node_id,
                          "direction": direction},
                 subject=subject, role=role, trust=trust)
    result = []
    for e in _load_edges():
        if direction in ("out", "both") and e["from_id"] == node_id:
            result.append((e, e["to_id"]))
        if direction in ("in", "both") and e["to_id"] == node_id:
            result.append((e, e["from_id"]))
    return result


def verify_node(node):
    """يتحقق من hash عقدة."""
    n = Node.from_dict(node)
    expected = node.get("hash")
    if expected is None:
        return False
    return n.compute_hash() == expected


def verify_edge(edge):
    """يتحقق من hash خيط."""
    e = Edge.from_dict(edge)
    expected = edge.get("hash")
    if expected is None:
        return False
    return e.compute_hash() == expected


def verify_all():
    """يتحقق من سلامة الشبكة."""
    nodes = _load_nodes()
    edges = _load_edges()
    bad_nodes = [n["node_id"] for n in nodes if not verify_node(n)]
    bad_edges = [e["edge_id"] for e in edges if not verify_edge(e)]
    return {
        "nodes": {"total": len(nodes), "invalid": bad_nodes},
        "edges": {"total": len(edges), "invalid": bad_edges},
        "ok": not bad_nodes and not bad_edges,
    }


def stats():
    """إحصائيات الشبكة."""
    nodes = _load_nodes()
    edges = _load_edges()
    relations = {}
    for e in edges:
        relations[e.get("relation", "related")] = \
            relations.get(e.get("relation", "related"), 0) + 1
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "max_nodes": MAX_NODES,
        "max_edges": MAX_EDGES,
        "relations": relations,
    }


if __name__ == "__main__":
    import json as _json
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(_json.dumps(stats(), indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "verify":
        print(_json.dumps(verify_all(), indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m memory.semantic.graph [stats|verify]")
