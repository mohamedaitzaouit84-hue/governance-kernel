"""G0.18 — Cooperative Task Success (H20).

Criterion: 50/50 cooperative tasks complete with zero kernel modifications.

Uses FakeAgents (same interface as V0.5 agents: name, subject_id, trust)
to isolate V0.6 protocol from V0.5 agent internals.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.coordinator import Coordinator


class FakeAgent:
    """Minimal agent stand-in (V0.5 compatible interface)."""
    def __init__(self, name, subject_id, trust):
        self.name = name
        self.subject_id = subject_id
        self.trust = trust


N_TASKS = 50


def main():
    results = []
    for i in range(N_TASKS):
        reader = FakeAgent("FileAgent", "file_agent_1", 0.70)
        computer = FakeAgent("ComputeAgent", "compute_agent_1", 0.65)
        writer = FakeAgent("QueryAgent", "query_agent_1", 0.55)

        c = Coordinator(reader, computer, writer)

        task = {
            "path": "input_{}.txt".format(i),
            "a": i,
            "b": i + 1,
            "output": "output_{}.txt".format(i),
        }
        out = c.run_task(task)

        # Expected sum
        expected_sum = task["a"] + task["b"]

        ok = (
            out["ok"] is True
            and out["reason"] is None
            and out["result"]["compute_result"]["sum"] == expected_sum
            and out["result"]["written_to"] == task["output"]
            and len(out["cycles"]) == 1
        )
        results.append((i, ok))

    passed = sum(1 for _, ok in results if ok)
    failed = [i for i, ok in results if not ok]

    print("  Run {} cooperative tasks".format(N_TASKS))
    print("  Passed: {}/{}".format(passed, N_TASKS))
    if failed:
        print("  Failed tasks: {}".format(failed[:10]))

    if passed == N_TASKS:
        print("G0.18: CLOSED ({}/{})".format(passed, N_TASKS))
        return 0
    else:
        print("G0.18: FAILED ({}/{})".format(passed, N_TASKS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
