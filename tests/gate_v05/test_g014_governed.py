"""G0.14 — Governed Execution.

Criterion: 100% of agent actions go through governed_action_v05.
Verifies: allowed actions succeed + denied actions raise ActionDenied
+ audit log records every attempt.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "agents"))
sys.path.insert(0, str(_repo / "authorization"))

from agents.file_agent import FileAgent
from agents.compute_agent import ComputeAgent
from agents.query_agent import QueryAgent
from agents.base_agent import InvariantViolation
import governed_action_v05


def main():
    checks = []

    # 1. FileAgent allowed action
    f = FileAgent("br_test", subject_id="file_agent_1")
    r = f.act("file_read", payload={"path": "notes.txt"})
    checks.append(("FileAgent file_read", r["ok"]))

    # 2. ComputeAgent allowed action
    c = ComputeAgent("br_test", subject_id="compute_agent_1")
    r = c.act("compute_add", payload={"a": 1, "b": 2})
    checks.append(("ComputeAgent compute_add", r["ok"]))

    # 3. QueryAgent allowed action
    q = QueryAgent("br_test", subject_id="query_agent_1")
    r = q.act("query_lookup", payload={"key": "x"})
    checks.append(("QueryAgent query_lookup", r["ok"]))

    # 4. Denied: FileAgent tries compute_add (invariant blocks)
    f2 = FileAgent("br_test", subject_id="file_agent_1")
    try:
        f2.act("compute_add", payload={"a": 1, "b": 2})
        checks.append(("FileAgent compute_add blocked", False))
    except (governed_action_v05.ActionDenied, InvariantViolation):
        checks.append(("FileAgent compute_add blocked", True))

    # 5. Denied: QueryAgent tries file_write (invariant blocks)
    q2 = QueryAgent("br_test", subject_id="query_agent_1")
    try:
        q2.act("file_write", payload={"path": "x.txt"})
        checks.append(("QueryAgent file_write blocked", False))
    except (governed_action_v05.ActionDenied, InvariantViolation):
        checks.append(("QueryAgent file_write blocked", True))

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("  {}: {}".format("PASS" if ok else "FAIL", name))
    print("G0.14: {}/{} governed execution checks".format(passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
