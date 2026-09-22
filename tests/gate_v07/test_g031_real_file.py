"""G0.31 — Real FileAgent in Coordinator (H23 part 1).

Criterion: 10/10 tasks succeed with real FileAgent as reader.

Each task:
  - Creates 3 fresh real agents (FileAgent, ComputeAgent, QueryAgent)
  - Runs CoordinatorV2
  - Verifies the FileAgent produced 'file_read' action

Read-only. Does NOT modify V0.5 or V0.6 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.file_agent import FileAgent
from agents.compute_agent import ComputeAgent
from agents.query_agent import QueryAgent
from agents.multi.coordinator_v2 import CoordinatorV2

N_TASKS = 10


def _run_one(i):
    reader = FileAgent("br_g31", subject_id="file_agent_1")
    computer = ComputeAgent("br_g31", subject_id="compute_agent_1")
    writer = QueryAgent("br_g31", subject_id="query_agent_1")

    c = CoordinatorV2(reader, computer, writer, branch_id="br_g31")

    task = {
        "path": "test_{}.txt".format(i),
        "a": i,
        "b": i + 1,
        "output": "out_{}.txt".format(i),
    }
    out = c.run_task(task)

    # Verify: task ok AND file_read was the read action
    if not out["ok"]:
        return False, "task failed: {}".format(out.get("reason"))
    fc = out["result"]["file_content"]
    if not fc or fc.get("action") != "file_read":
        return False, "file_read not called: {}".format(fc)
    return True, None


def main():
    passed = 0
    failed = []
    for i in range(N_TASKS):
        try:
            ok, msg = _run_one(i)
        except Exception as e:
            ok = False
            msg = "{}: {}".format(type(e).__name__, e)
        if ok:
            passed += 1
        else:
            failed.append((i, msg))

    print("  Tasks with real FileAgent: {}/{}".format(passed, N_TASKS))
    if failed:
        for i, m in failed[:5]:
            print("    task {}: {}".format(i, m))

    if passed == N_TASKS:
        print("G0.31: CLOSED ({}/{})".format(passed, N_TASKS))
        return 0
    else:
        print("G0.31: FAILED ({}/{})".format(passed, N_TASKS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
