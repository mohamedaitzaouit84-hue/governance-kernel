"""register_agents.py — Register V0.5 agents as branches.

For each agent, creates a branch in branch_registry:
  - name:      subject_id (e.g. file_agent_1)
  - kind:      filesystem / compute / query
  - permissions: matching the role in v0.5_agents.yaml
  - owner_signature_hex: signed by root (Trust Anchor)

Idempotent: skips if branch already registered.

Run:  python agents/register_agents.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent
sys.path.insert(0, str(_repo / "authorization"))
sys.path.insert(0, str(_repo / "seed"))
sys.path.insert(0, str(_repo / "audit"))

import branch_registry
import root
import append_only_log as audit


# Agent specifications — must match v0.5_agents.yaml roles.
AGENT_SPECS = [
    {
        "name": "file_agent_1",
        "kind": "filesystem",
        "permissions": [
            "file_read", "file_list", "file_write", "file_delete",
        ],
    },
    {
        "name": "compute_agent_1",
        "kind": "compute",
        "permissions": [
            "compute_add", "compute_sub", "compute_mul", "compute_div",
        ],
    },
    {
        "name": "query_agent_1",
        "kind": "query",
        "permissions": [
            "query_lookup", "query_count", "query_verify",
        ],
    },
]


def _already_registered(name):
    for r in branch_registry.list_branches():
        if r.get("name") == name:
            return r.get("branch_id")
    return None


def register_one(spec):
    """Register one agent. Returns dict with ok/branch_id/reason."""
    existing = _already_registered(spec["name"])
    if existing:
        return {"ok": True, "branch_id": existing, "skipped": True}

    perms = sorted(set(spec["permissions"]))

    # Owner signs the commitment
    commitment = branch_registry.commitment(
        spec["name"], spec["kind"], perms
    )
    signature = root.sign(commitment)
    sig_hex = signature.hex()

    result = branch_registry.register(
        name=spec["name"],
        kind=spec["kind"],
        requested_permissions=perms,
        owner_signature_hex=sig_hex,
    )
    return result


def main():
    print("=== V0.5 agent registration ===")
    print("Owner fingerprint:", root.fingerprint()[:16], "...")
    print()
    results = []
    for spec in AGENT_SPECS:
        r = register_one(spec)
        results.append((spec["name"], r))
        status = "REGISTERED" if r.get("ok") and not r.get("skipped") \
            else ("SKIPPED" if r.get("skipped") else "FAILED")
        print("  {:18s}  {}".format(spec["name"], status))
        if not r.get("ok"):
            print("    reason:", r.get("reason"))
    print()
    ok_count = sum(1 for _, r in results if r.get("ok"))
    print("Registered: {}/3".format(ok_count))
    audit.append("v05_agents_registered", {
        "total": len(AGENT_SPECS),
        "ok": ok_count,
        "names": [s["name"] for s in AGENT_SPECS],
    })
    return 0 if ok_count == len(AGENT_SPECS) else 1


if __name__ == "__main__":
    sys.exit(main())
