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
    ("G0.28 Cycle Time",            "test_g028_cycle_time.py"),
    ("G0.29 Memory Bound",          "test_g029_memory.py"),
    ("G0.30 Throughput",            "test_g030_throughput.py"),
    ("G0.31 Real FileAgent",        "test_g031_real_file.py"),
    ("G0.32 Real ComputeAgent",     "test_g032_real_compute.py"),
    ("G0.33 Real QueryAgent",       "test_g033_real_query.py"),
    ("G0.34 V0.5 Untouched",        "test_g034_v05_untouched.py"),
    ("G0.35 Delegation Issued",     "test_g035_delegation_issued.py"),
    ("G0.36 Delegation Expires",    "test_g036_delegation_expires.py"),
    ("G0.37 Delegation Revoked",    "test_g037_delegation_revoked.py"),
    ("G0.39 Path Portability",      "test_g039_path_portability.py"),
    ("G0.40 Path Port Audit",       "test_g040_path_portability_audit.py"),
]


def main():
    # Auto-bootstrap if needed (fresh clone support)
    import subprocess as _sp
    import sys as _sys
    _repo = Path(__file__).resolve().parent.parent.parent
    _bs = _repo / "bootstrap.py"
    if _bs.exists():
        _sp.call([_sys.executable, str(_bs)], cwd=str(_repo))
        print()

    print("=" * 60)
    print("V0.7 — Red Team + Performance + Real Agents + Delegation — Gate Report")
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
    print("V0.7 gates: {}/{} closed".format(passed, len(TESTS)))
    if passed == len(TESTS):
        print("--> V0.7.1 + V0.7.2 + V0.7.3 + V0.7.4 CLOSED")
    elif passed >= 5:
        print("--> V0.7 PARTIAL ({} findings pending)".format(
            len(TESTS) - passed))
    else:
        print("--> V0.7 FAILED (see JOURNEY.md)")
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
