"""V0.5 gate runner — G0.13 through G0.17."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

TESTS = [
    ("G0.13 Agent Registration", "test_g013_registration.py"),
    ("G0.14 Governed Execution", "test_g014_governed.py"),
    ("G0.15 Trust Dynamics",     "test_g015_trust.py"),
    ("G0.16 Invariant Enforce",  "test_g016_invariants.py"),
    ("G0.17 Kill Switch",        "test_g017_killswitch.py"),
]


def main():
    print("=" * 50)
    print("V0.5 — Gate Report")
    print("=" * 50)
    results = []
    for label, fname in TESTS:
        print()
        print("--- {} ---".format(label))
        rc = subprocess.call([sys.executable, str(HERE / fname)])
        results.append((label, rc == 0))

    passed = sum(1 for _, ok in results if ok)
    print()
    print("=" * 50)
    print("Aggregate")
    print("=" * 50)
    for label, ok in results:
        print("  {:30s}  {}".format(label, "CLOSED" if ok else "FAILED"))
    print()
    print("V0.5 gates: {}/5 closed".format(passed))
    if passed == 5:
        print("--> V0.5 CLOSED")
    elif passed == 4:
        print("--> V0.5 PARTIAL (V0.5.1)")
    else:
        print("--> V0.5 FAILED (see JOURNEY.md)")
    return 0 if passed == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
