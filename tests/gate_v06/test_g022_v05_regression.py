"""G0.22 — V0.5 Regression (H22 part 2).

Criterion: V0.5 gate suite = 5/5 closed after V0.6 additions.

Why this test matters:
  V0.6 added agents/multi/ and consensus/journal.jsonl.
  V0.6 MUST NOT alter any V0.5 behavior.

Approach:
  Run tests/gate_v05/run_all.py as a subprocess.
  Parse output for "5/5" and "V0.5 CLOSED".

No external dependencies.
"""
import sys
import subprocess
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

V05_RUNNER = _repo / "tests" / "gate_v05" / "run_all.py"


def main():
    if not V05_RUNNER.exists():
        print("  ERROR: V0.5 runner not found at {}".format(V05_RUNNER))
        print("G0.22: FAILED (missing V0.5 runner)")
        return 1

    print("  Running V0.5 gate suite (subprocess)...")
    result = subprocess.run(
        [sys.executable, str(V05_RUNNER)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr

    # Look for "V0.5 gates: 5/5 closed" line
    saw_5_of_5 = False
    saw_closed = False
    for line in output.splitlines():
        if "V0.5 gates: 5/5 closed" in line:
            saw_5_of_5 = True
        if "V0.5 CLOSED" in line:
            saw_closed = True

    print("  saw 5/5 gates: {}".format(saw_5_of_5))
    print("  saw V0.5 CLOSED: {}".format(saw_closed))

    if saw_5_of_5 and saw_closed:
        print("G0.22: CLOSED (V0.5 remains 5/5)")
        return 0
    else:
        print("G0.22: FAILED")
        print("  --- last 25 lines of V0.5 output ---")
        for line in output.splitlines()[-25:]:
            print("  " + line)
        return 1


if __name__ == "__main__":
    sys.exit(main())
