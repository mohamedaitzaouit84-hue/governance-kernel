"""G0.21 — V0.4 Regression (H22 part 1).

Criterion: V0.4 attack suite PRI = 1.0000 unchanged after V0.6.

Why this test matters:
  H22 says V0.6 does not break prior versions.
  V0.4 tested 54 attacks with 3 systems (baseline-A, baseline-B, kernel).
  V0.6 added files (agents/multi/, consensus/journal.jsonl) but
  MUST NOT alter any V0.4 behavior.

Approach:
  Run tests/gate_v04/run_all.py as a subprocess.
  Parse output for kernel PRI. Assert 1.0000.

No external dependencies.
"""
import sys
import subprocess
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

V04_RUNNER = _repo / "tests" / "gate_v04" / "run_all.py"
EXPECTED_PRI = "1.0000"


def main():
    if not V04_RUNNER.exists():
        print("  ERROR: V0.4 runner not found at {}".format(V04_RUNNER))
        print("G0.21: FAILED (missing V0.4 runner)")
        return 1

    print("  Running V0.4 attack suite (subprocess)...")
    result = subprocess.run(
        [sys.executable, str(V04_RUNNER)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr

    # The V0.4 runner prints a line like:
    #   "VERDICT: Kernel PRI = 1.0000  (threshold 0.95)"
    # We search for the kernel PRI value.
    kernel_pri = None
    for line in output.splitlines():
        if "Kernel PRI" in line and "=" in line:
            # Extract the number after "="
            parts = line.split("=")
            if len(parts) >= 2:
                val = parts[1].strip().split()[0].strip()
                kernel_pri = val
                break

    print("  Kernel PRI (parsed): {}".format(kernel_pri))
    print("  Expected:            {}".format(EXPECTED_PRI))

    if kernel_pri == EXPECTED_PRI:
        print("G0.21: CLOSED (V0.4 PRI unchanged = {})".format(EXPECTED_PRI))
        return 0
    else:
        print("G0.21: FAILED (expected {}, got {})".format(EXPECTED_PRI, kernel_pri))
        # Show last 20 lines for debugging
        print("  --- last 20 lines of V0.4 output ---")
        for line in output.splitlines()[-20:]:
            print("  " + line)
        return 1


if __name__ == "__main__":
    sys.exit(main())
