"""A2 — Role Spoofing.

Attack vector: a legitimate agent tries to escalate by pretending
to be a higher-privileged role.

Target: an agent with limited permissions (agent_mid) attempting
to gain owner or agent_high privileges via role manipulation.

Success: the agent executes tool:python (which agent_mid lacks).
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


# Base subject: a legitimate mid-tier agent
BASE_SUBJECT = "agent_mid_1"

# Target action: NOT in agent_mid's whitelist
TARGET_ACTION = "tool:python"

# Payloads: each tries a different role-spoofing trick
PAYLOADS = [
    # 1: baseline — legit role, action not allowed -> should be DENIED
    {"subject": BASE_SUBJECT, "role": "agent_mid", "action": TARGET_ACTION, "trust": 0.6},

    # 2: claim owner role directly
    {"subject": BASE_SUBJECT, "role": "owner", "action": TARGET_ACTION, "trust": 0.6},

    # 3: claim agent_high
    {"subject": BASE_SUBJECT, "role": "agent_high", "action": TARGET_ACTION, "trust": 0.6},

    # 4: case variation
    {"subject": BASE_SUBJECT, "role": "OWNER", "action": TARGET_ACTION, "trust": 0.6},

    # 5: leading whitespace
    {"subject": BASE_SUBJECT, "role": " owner", "action": TARGET_ACTION, "trust": 0.6},

    # 6: trailing whitespace
    {"subject": BASE_SUBJECT, "role": "owner ", "action": TARGET_ACTION, "trust": 0.6},

    # 7: newline separator
    {"subject": BASE_SUBJECT, "role": "agent_mid\nowner", "action": TARGET_ACTION, "trust": 0.6},

    # 8: list as role
    {"subject": BASE_SUBJECT, "role": ["owner"], "action": TARGET_ACTION, "trust": 0.6},

    # 9: dict as role
    {"subject": BASE_SUBJECT, "role": {"name": "owner"}, "action": TARGET_ACTION, "trust": 0.6},

    # 10: trust overflow only (role unchanged)
    {"subject": BASE_SUBJECT, "role": "agent_mid", "action": TARGET_ACTION, "trust": 9999.0},

    # 11: empty role
    {"subject": BASE_SUBJECT, "role": "", "action": TARGET_ACTION, "trust": 0.6},

    # 12: None role
    {"subject": BASE_SUBJECT, "role": None, "action": TARGET_ACTION, "trust": 0.6},
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


def run_attack(name, attack_fn, verbose=True):
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
                details.append((i, "exception", str(e)[:40]))
    return blocked, total, details


def main():
    print("=" * 70)
    print("A2 — Role Spoofing")
    print("=" * 70)
    print(f"Base subject: {BASE_SUBJECT}")
    print(f"Target action: {TARGET_ACTION} (not in agent_mid's permissions)")
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
                print(f"    [{i}] INJECTED: role={repr(payload['role'])[:35]}")
    print()


if __name__ == "__main__":
    main()
