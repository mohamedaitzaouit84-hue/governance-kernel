"""A3 — Confused Deputy.

Attack vector: an agent with elevated privileges (agent_high)
executes an action on behalf of a low-privilege agent (agent_low).

Success criterion: the low-privilege agent obtains an action it
could not perform directly.

Test scenarios:
- Low agent sends request "on behalf of" high agent
- High agent submits with low agent's subject_id but its own role
- Chain: low -> high -> gate
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


# Low-privilege agent
LOW_SUBJECT = "agent_low_1"
LOW_ROLE = "agent_low"

# Target action NOT in agent_low's permissions
TARGET_ACTION = "tool:python"


PAYLOADS = [
    # 1: baseline — low agent tries directly -> should be DENIED
    {"subject": LOW_SUBJECT, "role": LOW_ROLE, "action": TARGET_ACTION, "trust": 0.3},

    # 2: low agent claims high role (confused deputy foundation)
    {"subject": LOW_SUBJECT, "role": "agent_high", "action": TARGET_ACTION, "trust": 0.3},

    # 3: high agent executes for low subject
    {"subject": LOW_SUBJECT, "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 4: subject has "delegated_by" pattern in name
    {"subject": "agent_low_1_delegated_by_agent_high", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 5: subject looks like high but role is low
    {"subject": "agent_high_1", "role": LOW_ROLE, "action": TARGET_ACTION, "trust": 0.3},

    # 6: both subject and role look high, but trust is low
    {"subject": "agent_high_1", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.1},

    # 7: subject has both roles in name
    {"subject": "agent_low_1|agent_high", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 8: nested delegation
    {"subject": "agent_low_1->agent_high", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 9: unknown subject, high role
    {"subject": "unknown_deputy", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 10: empty subject, high role
    {"subject": "", "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 11: subject = None, high role
    {"subject": None, "role": "agent_high", "action": TARGET_ACTION, "trust": 0.9},

    # 12: subject = high role name, role = low (reverse)
    {"subject": "agent_high_1", "role": LOW_ROLE, "action": TARGET_ACTION, "trust": 0.9},
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
            role=payload["role"],
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
    print("A3 — Confused Deputy")
    print("=" * 70)
    print(f"Low subject: {LOW_SUBJECT} ({LOW_ROLE})")
    print(f"Target: {TARGET_ACTION}")
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
                subj = str(payload['subject'])[:25]
                role = str(payload['role'])[:15]
                print(f"    [{i}] INJECTED: subj={subj} role={role}")
    print()


if __name__ == "__main__":
    main()
