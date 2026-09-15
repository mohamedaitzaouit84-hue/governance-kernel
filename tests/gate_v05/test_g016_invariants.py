"""G0.16 — Invariant Enforcement (H14).

Criterion: 100% of invariant violations detected + agent isolated.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "agents"))

from agents.file_agent import FileAgent
from agents.compute_agent import ComputeAgent
from agents.query_agent import QueryAgent
from agents.base_agent import InvariantViolation


def _expect_blocked(agent, action, payload):
    try:
        agent.act(action, payload=payload)
        return False, "not blocked"
    except InvariantViolation as e:
        return True, str(e)
    except Exception as e:
        return False, "wrong exception: " + type(e).__name__


def main():
    checks = []

    # 1. FileAgent escape via ..
    f = FileAgent("br_t", subject_id="file_agent_1")
    ok, _ = _expect_blocked(f, "file_write", {"path": "../etc"})
    checks.append(("FileAgent .. escape blocked", ok))
    checks.append(("FileAgent isolated after violation", f.isolated is True))
    checks.append(("FileAgent trust reset to 0.00", f.trust == 0.00))

    # 2. FileAgent absolute path
    f2 = FileAgent("br_t", subject_id="file_agent_1")
    ok, _ = _expect_blocked(f2, "file_read", {"path": "/etc/passwd"})
    checks.append(("FileAgent /etc escape blocked", ok))

    # 3. FileAgent wrong action
    f3 = FileAgent("br_t", subject_id="file_agent_1")
    ok, _ = _expect_blocked(f3, "compute_add", {"a": 1, "b": 2})
    checks.append(("FileAgent compute_add blocked", ok))

    # 4. ComputeAgent non-numeric
    c = ComputeAgent("br_t", subject_id="compute_agent_1")
    ok, _ = _expect_blocked(c, "compute_add", {"a": "x", "b": 2})
    checks.append(("ComputeAgent non-numeric blocked", ok))
    checks.append(("ComputeAgent isolated", c.isolated is True))

    # 5. QueryAgent forbidden key
    q = QueryAgent("br_t", subject_id="query_agent_1")
    ok, _ = _expect_blocked(q, "query_lookup", {"key": "x", "write": True})
    checks.append(("QueryAgent forbidden key blocked", ok))

    # 6. QueryAgent wrong action
    q2 = QueryAgent("br_t", subject_id="query_agent_1")
    ok, _ = _expect_blocked(q2, "file_read", {"path": "x"})
    checks.append(("QueryAgent file_read blocked", ok))

    # 7. Isolated agent cannot act
    try:
        f.act("file_read", payload={"path": "x.txt"})
        checks.append(("Isolated agent refuses action", False))
    except InvariantViolation:
        checks.append(("Isolated agent refuses action", True))

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("  {}: {}".format("PASS" if ok else "FAIL", name))
    print("G0.16: {}/{} invariant checks".format(passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
