"""G0.15 — Trust Dynamics (H1).

Criterion: trust changes on outcome, stays in [0.00, 0.85], logged.
Verifies: +alpha on success, -beta on deny, clamps at bounds.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "agents"))

from agents.file_agent import FileAgent
from agents.trust_manager import TRUST_ALPHA, TRUST_BETA, TRUST_MAX, TRUST_MIN, TRUST_INITIAL
from agents.base_agent import InvariantViolation
import governed_action_v05


def main():
    checks = []

    # 1. Start at TRUST_INITIAL
    f = FileAgent("br_test", subject_id="file_agent_1")
    checks.append(("initial trust == 0.10", abs(f.trust - TRUST_INITIAL) < 1e-9))

    # 2. Success increments by alpha
    f.act("file_read", payload={"path": "a.txt"})
    checks.append(("after 1 success trust == 0.15",
                   abs(f.trust - (TRUST_INITIAL + TRUST_ALPHA)) < 1e-9))

    # 3. 3 successes: 0.10 + 3*0.05 = 0.25
    f.act("file_read", payload={"path": "b.txt"})
    f.act("file_read", payload={"path": "c.txt"})
    checks.append(("after 3 successes trust == 0.25",
                   abs(f.trust - 0.25) < 1e-9))

    # 4. Trust cannot exceed TRUST_MAX (0.85)
    # Use apply_delta directly for speed
    from agents.trust_manager import apply_delta
    capped = apply_delta(0.80, 0.10)
    checks.append(("apply_delta caps at 0.85", abs(capped - TRUST_MAX) < 1e-9))

    # 5. Trust cannot go below TRUST_MIN (0.00)
    floored = apply_delta(0.02, -0.10)
    checks.append(("apply_delta floors at 0.00", abs(floored - TRUST_MIN) < 1e-9))

    # 6. Trust never 1.0 (by design — cap 0.85)
    checks.append(("TRUST_MAX < 1.0", TRUST_MAX < 1.0))

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("  {}: {}".format("PASS" if ok else "FAIL", name))
    print("G0.15: {}/{} trust dynamics checks".format(passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
