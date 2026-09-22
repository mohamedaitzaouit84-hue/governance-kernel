"""G0.33 — Real QueryAgent in Coordinator (H23 part 3).

Criterion: 10/10 tasks succeed with real QueryAgent as writer.

Each task:
  - Creates 3 fresh real agents
  - Runs CoordinatorV2
  - Verifies the QueryAgent produced 'query_lookup' action

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
    reader = FileAgent("br_g33", subject_id="file_agent_1")
    computer = ComputeAgent("br_g33", subject_id="compute_agent_1")
    writer = QueryAgent("br_g33", subject_id="query_agent_1")

    c = CoordinatorV2(reader, computer, writer, branch_id="br_g33")

    task = {
        "path": "q_{}.txt".format(i),
        "a": i,
        "b": i,
        "output": "key_{}".format(i),
    }
    out = c.run_task(task)

    if not out["ok"]:
        return False, "task failed: {}".format(out.get("reason"))
    wt = out["result"]["written_to"]
    if not wt or wt.get("action") != "query_lookup":
        return False, "query_lookup not called: {}".format(wt)
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

    print("  Tasks with real QueryAgent: {}/{}".format(passed, N_TASKS))
    if failed:
        for i, m in failed[:5]:
            print("    task {}: {}".format(i, m))

    if passed == N_TASKS:
        print("G0.33: CLOSED ({}/{})".format(passed, N_TASKS))
        return 0
    else:
        print("G0.33: FAILED ({}/{})".format(passed, N_TASKS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
