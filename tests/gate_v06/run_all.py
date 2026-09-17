"""V0.6 gate runner — G0.18 through G0.22."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

TESTS = [
    ("G0.18 Cooperative Task",     "test_g018_cooperation.py"),
    ("G0.19 Single-agent Control", "test_g019_consensus.py"),
    ("G0.20 Double Attestation",   "test_g020_double_attest.py"),
    ("G0.21 V0.4 Regression",      "test_g021_v04_regression.py"),
    ("G0.22 V0.5 Regression",      "test_g022_v05_regression.py"),
]


def main():
    print("=" * 60)
    print("V0.6 — Multi-Agent Governance — Gate Report")
    print("=" * 60)
    results = []
    for label, fname in TESTS:
        print()
        print("--- {} ---".format(label))
        rc = subprocess.call([sys.executable, str(HERE / fname)])
        results.append((label, rc == 0))

    passed = sum(1 for _, ok in results if ok)
    print()
    print("=" * 60)
    print("Aggregate")
    print("=" * 60)
    for label, ok in results:
        print("  {:32s}  {}".format(label, "CLOSED" if ok else "FAILED"))
    print()
    print("V0.6 gates: {}/5 closed".format(passed))
    if passed == 5:
        print("--> V0.6 CLOSED")
    elif passed == 4:
        print("--> V0.6 PARTIAL (V0.6.1)")
    else:
        print("--> V0.6 FAILED (see JOURNEY.md)")
    return 0 if passed == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
