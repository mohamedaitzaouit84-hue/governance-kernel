"""subject_registry.py — Trusted mapping of subject_id -> (role, trust).

The policy engine reads role/trust from here, NOT from the request.
This prevents Confused Deputy: a caller cannot claim a role it does not own.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent

sys.path.insert(0, str(_root / "seed"))
sys.path.insert(0, str(_root / "audit"))

import root
import append_only_log as audit

KERNEL_DIR = _root
REGISTRY_FILE = KERNEL_DIR / "authorization" / "subjects.json"


def _default_registry():
    """Initial registry — created on first use."""
    return {
        "version": "0.4.1",
        "subjects": {
            "owner": {"role": "owner", "trust": 1.0},
            "system": {"role": "system", "trust": 0.9},
            "agent_high_1": {"role": "agent_high", "trust": 0.8},
            "agent_mid_1": {"role": "agent_mid", "trust": 0.6},
            "agent_low_1": {"role": "agent_low", "trust": 0.3},
        },
    }


def load():
    """Load the registry. Creates default if missing."""
    import json
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = _default_registry()
        REGISTRY_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        audit.append("subject_registry_created", {"n_subjects": len(data["subjects"])})
        return data
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def lookup(subject_id):
    """Return {'role', 'trust'} for a subject, or None."""
    if not isinstance(subject_id, str) or not subject_id:
        return None
    reg = load()
    entry = reg.get("subjects", {}).get(subject_id)
    if entry is None:
        return None
    return {"role": entry["role"], "trust": entry["trust"]}


def is_registered(subject_id):
    return lookup(subject_id) is not None
