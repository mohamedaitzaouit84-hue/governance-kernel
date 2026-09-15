"""policy_extension.py — Layered policy loader (P-Q11).

Loads the SIGNED base policy via policy_store.load(), then merges
one or more extension files on top. Base file is never modified.

Merge semantics:
    - roles: extension wins on name conflict
    - limits: extension wins on key conflict
    - default_decision: inherited from base
    - version: inherited from base

The base policy's signature is enforced by policy_store.load().
Extensions are not signed (yet) — they are V0.5-only additions.

See docs/PATTERNS.md P-Q11.
"""

import sys
from pathlib import Path
import yaml

_here = Path(__file__).resolve().parent
_repo = _here.parent
sys.path.insert(0, str(_repo / "policy"))
sys.path.insert(0, str(_repo / "audit"))

import policy_store
import append_only_log as audit

EXTENSIONS_DIR = _repo / "policy" / "policies"


def load_extension(name):
    """Load one extension file. Returns dict, or None if missing."""
    p = EXTENSIONS_DIR / name
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def load_extended(*extension_names):
    """Load signed base + merge extensions in order.

    Base is loaded via policy_store.load() — signature enforced.
    Extensions are merged on top (extension wins).
    Returns a policy dict ready for PolicyEngine(policy=...).
    """
    base = policy_store.load()

    merged = {
        "version": base.get("version", "unknown"),
        "default_decision": base.get("default_decision", "deny"),
        "roles": dict(base.get("roles", {})),
        "limits": dict(base.get("limits", {})),
        "memory_limits": dict(base.get("memory_limits", {})),
    }

    extensions_applied = []
    for ext_name in extension_names:
        ext = load_extension(ext_name)
        if ext is None:
            continue
        extensions_applied.append(ext_name)
        for rname, rdef in ext.get("roles", {}).items():
            merged["roles"][rname] = rdef
        for k, v in ext.get("limits", {}).items():
            merged["limits"][k] = v
        for k, v in ext.get("memory_limits", {}).items():
            merged["memory_limits"][k] = v

    audit.append("policy_extended", {
        "base_version": base.get("version"),
        "extensions": extensions_applied,
        "total_roles": len(merged["roles"]),
    })
    return merged
