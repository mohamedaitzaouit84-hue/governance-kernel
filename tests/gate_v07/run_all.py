"""V0.7.1 gate runner — Red Team."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

TESTS = [
    ("G0.23 Sybil Resistance",     "test_g023_sybil.py"),
    ("G0.24 Collusion Handling",   "test_g024_collusion.py"),
    ("G0.25 Timing Safety",        "test_g025_timing.py"),
    ("G0.26 Trust Bound",          "test_g026_trust_manipulation.py"),
    ("G0.27 Protocol Integrity",   "test_g027_protocol_bypass.py"),
    ("G0.ZZ Kernel Untouched",     "test_g0ZZ_kernel_untouched.py"),
]


def main():
    print("=" * 60)
    print("V0.7.1 — Red Team — Gate Report")
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
    print("V0.7.1 gates: {}/{} closed".format(passed, len(TESTS)))
    if passed == len(TESTS):
        print("--> V0.7.1 CLOSED")
    elif passed >= 5:
        print("--> V0.7.1 PARTIAL ({} findings pending)".format(
            len(TESTS) - passed))
    else:
        print("--> V0.7.1 FAILED (see JOURNEY.md)")
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
