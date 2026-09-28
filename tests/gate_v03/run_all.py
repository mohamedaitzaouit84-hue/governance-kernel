"""run_all.py — V0.3 consolidated test runner.

Runs 5 V0.3 gate tests. Aggregates CLOSED/FAILED status.

NOTE: V0.3 is documented as '2/3 gates' (docs/V0.3_SUMMARY.md,
2026-09-14):
  - G0.7 Policy Separation: HOLDS in noise; MAY FAIL in drift
    (see J-0.8.33 for a report inaccuracy in the drift value).
  - G0.9 Statistical Repeatability: CLOSED
  - G0.9 v2 (std): CLOSED
  - G0.9 v3 (same-seed): CLOSED
  - G0.11 Counterfactual: FAILED in drift (documented finding)

This runner is for manual verification. It is NOT in CI.
Reason: expected partial failures; CI must be binary.

Usage:
  python tests/gate_v03/run_all.py
Exit code: 0 if at least 3 gates closed, 1 otherwise.
"""
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent

TESTS = [
    ("G0.7 Policy Separation",          _here / "g07_policy_separation.py"),
    ("G0.9 Statistical Repeatability",  _here / "g09_statistical_repeatability.py"),
    ("G0.9 v2 Repeatability (std)",     _here / "g09_repeatability_v2.py"),
    ("G0.9 v3 Same-seed Repeatability", _here / "g09_repeatability_v3.py"),
    ("G0.11 Counterfactual",            _here / "g11_counterfactual.py"),
]


def run_test(name, path):
    if not path.exists():
        return name, "MISSING", ""
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(_repo),
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return name, "TIMEOUT", ""
    output = result.stdout + result.stderr
    if "CLOSED" in output:
        status = "CLOSED"
    elif "FAILED" in output or "MAY FAIL" in output:
        status = "FAILED"
    elif "HOLDS" in output:
        status = "CLOSED"
    else:
        status = "UNKNOWN"
    return name, status, output


def main():
    print("=" * 70)
    print("V0.3 — Consolidated Gate Report")
    print("=" * 70)
    print()
    print("Note: V0.3 is documented as '2/3 gates' (docs/V0.3_SUMMARY.md).")
    print("      See docs/GATES_v0.3_G07_report.md, JOURNEY J-0.8.33.")
    print()

    results = []
    for name, path in TESTS:
        print(f"--- {name} ---")
        n, status, output = run_test(name, path)
        if output:
            lines = output.strip().splitlines()
            for line in lines[-5:]:
                print("  " + line)
        else:
            print("  (no output)")
        print()
        results.append((name, status))

    print("=" * 70)
    print("Aggregate")
    print("=" * 70)
    closed = 0
    for name, status in results:
        print(f"  {name:40s} {status}")
        if status == "CLOSED":
            closed += 1

    total = len(TESTS)
    print()
    print(f"V0.3 gates: {closed}/{total} closed")
    if closed >= 3:
        print("--> V0.3 CLOSED (partial — see docs/V0.3_SUMMARY.md)")
        return 0
    else:
        print(f"--> V0.3 PARTIAL ({total - closed} failing)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
