"""memory/semantic/edge.py — خيط يربط عقدتين."""
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Dict


@dataclass
class Edge:
    edge_id: str
    from_id: str
    to_id: str
    relation: str = "related"
    weight: float = 1.0
    properties: Dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def compute_hash(self) -> str:
        payload = json.dumps({
            "id": self.edge_id,
            "from": self.from_id,
            "to": self.to_id,
            "relation": self.relation,
            "weight": self.weight,
        }, sort_keys=True, ensure_ascii=False,
            separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: dict) -> "Edge":
        return cls(
            edge_id=d["edge_id"],
            from_id=d["from_id"],
            to_id=d["to_id"],
            relation=d.get("relation", "related"),
            weight=float(d.get("weight", 1.0)),
            properties=d.get("properties", {}),
            created_at=d.get("created_at", ""),
        )

    def verify(self, expected_hash: str) -> bool:
        return self.compute_hash() == expected_hash
