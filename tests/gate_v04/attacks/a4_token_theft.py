"""A4 — Token Theft.

Attack vector: attacker obtains a valid subject_id (by guessing,
enumeration, or leak) and uses it without proper authorization.

Since V0.4.1, the gate checks the registry. So the attack tests:
- Does the registry prevent enumeration?
- Are there side-channels exposing valid subject_ids?
- Can a stolen subject_id be reused from a different context?

Success criterion: attacker executes an action with a stolen
subject_id when they should not.
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


# Simulated "leaked" subject from the registry
LEAKED_SUBJECTS = ["agent_high_1", "agent_mid_1", "owner", "system"]
# Guessed subjects
GUESSED_SUBJECTS = ["agent_high_2", "admin", "root", "agent_high", ""]


PAYLOADS = []

# A: legitimate leaked use (should be allowed — subject is real)
for s in LEAKED_SUBJECTS:
    PAYLOADS.append({
        "subject": s,
        "role": "any",
        "action": "tool:file_read",
        "trust": 0.0,
        "case": "leaked-valid",
    })

# B: guessed non-existent subjects (should be denied)
for s in GUESSED_SUBJECTS:
    PAYLOADS.append({
        "subject": s,
        "role": "any",
        "action": "tool:file_read",
        "trust": 0.0,
        "case": "guessed",
    })

# C: subject with injection attempt in name
PAYLOADS.append({
    "subject": "agent_high_1\x00admin",
    "role": "any",
    "action": "tool:file_read",
    "trust": 0.0,
    "case": "injection",
})
PAYLOADS.append({
    "subject": "agent_high_1\nadmin",
    "role": "any",
    "action": "tool:file_read",
    "trust": 0.0,
    "case": "injection",
})
PAYLOADS.append({
    "subject": " agent_high_1",
    "role": "any",
    "action": "tool:file_read",
    "trust": 0.0,
    "case": "injection",
})


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


def is_legitimate(payload):
    """Legit = a valid registered subject acting on its own behalf."""
    reg = load_registry()
    return payload["subject"] in reg.get("subjects", {})


def run_attack(name, attack_fn):
    """PRI: attacks blocked / attacks total, but only counting ILLEGITIMATE."""
    blocked = 0
    total = 0
    details = []
    for i, p in enumerate(PAYLOADS):
        legit = is_legitimate(p)
        if legit:
            continue  # skip legitimate uses
        total += 1
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
    print("A4 — Token Theft")
    print("=" * 70)
    print(f"Payloads: {len(PAYLOADS)} total")
    print(f"Legitimate (skipped): {sum(1 for p in PAYLOADS if is_legitimate(p))}")
    print(f"Illegitimate (tested): {sum(1 for p in PAYLOADS if not is_legitimate(p))}")
    print()

    systems = [
        ("Baseline-A (no gate)", attack_baseline_a),
        ("Baseline-B (whitelist)", attack_baseline_b),
        ("Kernel", attack_kernel),
    ]

    for name, fn in systems:
        blocked, total, details = run_attack(name, fn)
        pri = blocked / total if total > 0 else 1.0
        print(f"{name:30s}  blocked = {blocked}/{total}  PRI = {pri:.2f}")
        for i, status, payload in details:
            if status == "INJECTED":
                s = str(payload['subject'])[:30]
                print(f"    [{i}] INJECTED: subject={s!r} case={payload['case']}")
    print()


if __name__ == "__main__":
    main()
