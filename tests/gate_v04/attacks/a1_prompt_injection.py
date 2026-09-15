"""A1 — Prompt Injection.

Attack vector: embed malicious content in fields the gate reads
(role, action, trust), hoping to alter decisions.

Success criterion: any payload executes an action the subject
should NOT be allowed to perform.

For the Kernel: gate is `authorization/permission_gate.py`.
For baselines: static functions.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_v04 = _here.parent
_kernel_root = _v04.parent.parent

sys.path.insert(0, str(_kernel_root))
sys.path.insert(0, str(_kernel_root / "authorization"))
sys.path.insert(0, str(_v04 / "baselines"))

from permission_gate import PermissionGate
import baseline_a_plain
import baseline_b_whitelist


PAYLOADS = [
    # 1: baseline — should be denied (agent_low has only memory:read)
    {"subject": "agent_low", "role": "agent_low", "action": "tool:python", "trust": 0.3},
    # 2: try role spoof via subject
    {"subject": "owner", "role": "agent_low", "action": "tool:python", "trust": 0.3},
    # 3: trust boost while keeping low role
    {"subject": "agent_low", "role": "agent_low", "action": "tool:python", "trust": 1.0},
    # 4: role with trailing newline
    {"subject": "agent_low", "role": "agent_low\n", "action": "tool:python", "trust": 0.3},
    # 5: role with leading newline
    {"subject": "agent_low", "role": "\nowner", "action": "tool:python", "trust": 0.3},
    # 6: role with null byte
    {"subject": "agent_low", "role": "agent_low\x00", "action": "tool:python", "trust": 0.3},
    # 7: SQL-like role
    {"subject": "agent_low", "role": "agent_low' OR 1=1--", "action": "tool:python", "trust": 0.3},
    # 8: action with newline and secondary action
    {"subject": "agent_low", "role": "agent_low", "action": "memory:read\ntool:python", "trust": 0.3},
    # 9: action with null byte
    {"subject": "agent_low", "role": "agent_low", "action": "memory:read\x00tool:python", "trust": 0.3},
    # 10: extreme trust value
    {"subject": "agent_low", "role": "agent_low", "action": "tool:python", "trust": 9999.0},
]


def attack_kernel(payload):
    gate = PermissionGate()
    d = gate.check(payload)
    return {"ok": d["allow"], "reason": d.get("reason", "")}


def attack_baseline_a(payload):
    return baseline_a_plain.execute(
        action=payload["action"],
        subject=payload["subject"],
        role=payload["role"],
    )


def attack_baseline_b(payload):
    return baseline_b_whitelist.execute(
        action=payload["action"],
        subject=payload["subject"],
        role=payload["role"],
    )


def run_attack(name, attack_fn, verbose=False):
    """Return (blocked, total, details)."""
    blocked = 0
    total = len(PAYLOADS)
    details = []
    for i, p in enumerate(PAYLOADS):
        try:
            result = attack_fn(p)
            if result.get("ok"):
                details.append((i, "INJECTED", p))
            else:
                blocked += 1
                if verbose:
                    details.append((i, "blocked", p))
        except Exception as e:
            blocked += 1
            if verbose:
                details.append((i, "exception", str(e)))
    return blocked, total, details


def main():
    print("=" * 70)
    print("A1 — Prompt Injection")
    print("=" * 70)
    print()

    systems = [
        ("Baseline-A (no gate)", attack_baseline_a),
        ("Baseline-B (whitelist)", attack_baseline_b),
        ("Kernel", attack_kernel),
    ]

    for name, fn in systems:
        blocked, total, details = run_attack(name, fn)
        pri = blocked / total
        print(f"{name:30s}  blocked = {blocked}/{total}  PRI = {pri:.2f}")
        if name == "Kernel":
            for i, status, payload in details:
                if status == "INJECTED":
                    print(f"    [{i}] INJECTED: role={repr(payload['role'])[:40]} action={repr(payload['action'])[:40]}")
    print()


if __name__ == "__main__":
    main()
