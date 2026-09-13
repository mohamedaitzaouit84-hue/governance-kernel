"""memory/semantic/node.py — عقدة في الشبكة."""
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Dict


@dataclass
class Node:
    node_id: str
    label: str
    properties: Dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def compute_hash(self) -> str:
        payload = json.dumps({
            "id": self.node_id,
            "label": self.label,
            "properties": self.properties,
        }, sort_keys=True, ensure_ascii=False,
            separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: dict) -> "Node":
        return cls(
            node_id=d["node_id"],
            label=d["label"],
            properties=d.get("properties", {}),
            created_at=d.get("created_at", ""),
        )

    def verify(self, expected_hash: str) -> bool:
        return self.compute_hash() == expected_hash
