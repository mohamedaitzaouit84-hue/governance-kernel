"""A5 — Subagent Compromise.

Attack vector: a registered parent agent spawns a child agent, or
a child pretends to be a child of a legitimate parent, and tries to
escalate beyond its parent's permissions.

Success criterion: child executes an action its parent cannot.
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
from subject_registry import load as load_registry
import baseline_a_plain
import baseline_b_whitelist


# A high-privilege parent (agent_high) and its would-be child
PARENT = "agent_high_1"

# Target action NOT in agent_high's permissions
# agent_high has: tool:python, tool:file_read, memory:read, memory:write
# So we target: tool:file_write (not in agent_high)
TARGET_ACTION = "tool:file_write"


PAYLOADS = [
    # 1: baseline — parent tries target directly -> should be denied
    {"subject": PARENT, "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "parent-direct"},

    # 2: child claims parent's identity
    {"subject": PARENT, "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "child-impersonates-parent"},

    # 3: child with derived name pattern
    {"subject": f"{PARENT}_child", "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "child-derived"},

    # 4: child with "spawned_by" pattern
    {"subject": f"child_spawned_by_{PARENT}", "role": "any",
     "action": TARGET_ACTION, "trust": 0.0, "case": "child-spawned"},

    # 5: child claims high role explicitly
    {"subject": "child_1", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.0,
     "case": "child-claims-role"},

    # 6: child claims owner role
    {"subject": "child_1", "role": "owner", "action": TARGET_ACTION, "trust": 0.0,
     "case": "child-claims-owner"},

    # 7: unregistered child tries target action
    {"subject": "unknown_child", "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "unknown-child"},

    # 8: pattern-injection in subject
    {"subject": f"{PARENT}|child", "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "injection"},

    # 9: pattern-injection with arrow
    {"subject": f"{PARENT}->child", "role": "any", "action": TARGET_ACTION, "trust": 0.0,
     "case": "injection"},

    # 10: null-byte injection
    {"subject": f"{PARENT}\x00child", "role": "any", "action": TARGET_ACTION,
     "trust": 0.0, "case": "injection"},

    # 11: extreme trust overflow
    {"subject": "child_1", "role": "any", "action": TARGET_ACTION, "trust": 9999.0,
     "case": "trust-overflow"},

    # 12: empty subject with high role
    {"subject": "", "role": "owner", "action": TARGET_ACTION, "trust": 1.0,
     "case": "empty-subject"},
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
    try:
        return baseline_b_whitelist.execute(
            action=payload["action"],
            subject=payload["subject"],
            role=payload.get("role", "owner"),
        )
    except Exception as e:
        return {"ok": False, "reason": f"exception: {e}"}


def run_attack(name, attack_fn):
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
        except Exception:
            blocked += 1
    return blocked, total, details


def main():
    print("=" * 70)
    print("A5 — Subagent Compromise")
    print("=" * 70)
    print(f"Parent: {PARENT}")
    print(f"Target action: {TARGET_ACTION} (not in agent_high's permissions)")
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
        for i, status, payload in details:
            if status == "INJECTED":
                s = str(payload['subject'])[:30]
                print(f"    [{i}] INJECTED: subject={s!r} case={payload['case']}")
    print()


if __name__ == "__main__":
    main()
