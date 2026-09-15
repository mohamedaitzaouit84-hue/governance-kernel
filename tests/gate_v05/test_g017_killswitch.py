"""G0.17 — Kill Switch Respect.

Criterion: when kill switch active, all agents halt immediately.
Uses the existing control/kill_switch module. Restores state after test.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "agents"))
sys.path.insert(0, str(_repo / "control"))
sys.path.insert(0, str(_repo / "seed"))

from agents.file_agent import FileAgent
from agents.compute_agent import ComputeAgent
from agents.query_agent import QueryAgent
import governed_action_v05
import kill_switch
import root


def main():
    checks = []
    was_active = kill_switch.is_active()
    if was_active:
        print("  WARN: kill switch already active — aborting test")
        return 1

    # Trigger kill switch
    kill_switch.trigger(reason="v05 test", by="test_g017")
    checks.append(("kill switch active after trigger", kill_switch.is_active()))

    # 1. FileAgent halted
    f = FileAgent("br_t", subject_id="file_agent_1")
    try:
        f.act("file_read", payload={"path": "x.txt"})
        checks.append(("FileAgent halted", False))
    except governed_action_v05.ActionDenied as e:
        checks.append(("FileAgent halted", "kill switch" in str(e)))

    # 2. ComputeAgent halted
    c = ComputeAgent("br_t", subject_id="compute_agent_1")
    try:
        c.act("compute_add", payload={"a": 1, "b": 2})
        checks.append(("ComputeAgent halted", False))
    except governed_action_v05.ActionDenied as e:
        checks.append(("ComputeAgent halted", "kill switch" in str(e)))

    # 3. QueryAgent halted
    q = QueryAgent("br_t", subject_id="query_agent_1")
    try:
        q.act("query_lookup", payload={"key": "x"})
        checks.append(("QueryAgent halted", False))
    except governed_action_v05.ActionDenied as e:
        checks.append(("QueryAgent halted", "kill switch" in str(e)))

    # Clear kill switch — needs owner signature
    msg = "clear kill switch test"                    # str, not bytes
    sig = root.sign(msg.encode("utf-8"))              # encode for signing
    kill_switch.clear(signature_hex=sig.hex(), message=msg)  # pass str
    checks.append(("kill switch cleared", not kill_switch.is_active()))

    # 4. After clear, agents can act again
    f2 = FileAgent("br_t", subject_id="file_agent_1")
    try:
        f2.act("file_read", payload={"path": "x.txt"})
        checks.append(("FileAgent acts after clear", True))
    except Exception:
        checks.append(("FileAgent acts after clear", False))

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("  {}: {}".format("PASS" if ok else "FAIL", name))
    print("G0.17: {}/{} kill switch checks".format(passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
