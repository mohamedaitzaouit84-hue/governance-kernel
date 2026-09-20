"""G0.29 — Memory Bound (H31).

Criterion: 1000 cycles consume < 50 MB of additional RSS.

Method: measure VmRSS before/after 1000 cycles via
/proc/self/status. gc.collect() called before each measurement.

On Android/Termux, /proc/self/status is readable.
If unreadable, the test reports SKIPPED, not FAILED.

Read-only. Does not modify V0.6 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.benchmark.runner import (
    measure_memory,
    DEFAULT_TRUSTS,
)

THRESHOLD_MB = 50.0
N_CYCLES = 1000


def main():
    print("  Running {} cycles (RSS measurement)...".format(N_CYCLES))
    r = measure_memory(N_CYCLES, DEFAULT_TRUSTS)

    rss_before = r["rss_before_kb"]
    rss_after = r["rss_after_kb"]
    delta_kb = r["delta_kb"]

    print("  rss before: {} kB".format(rss_before))
    print("  rss after:  {} kB".format(rss_after))
    print("  delta:      {} kB".format(delta_kb))
    print("  threshold:  < {} MB".format(THRESHOLD_MB))

    if rss_before <= 0 or rss_after <= 0:
        print("G0.29: SKIPPED (RSS not readable on this platform)")
        print("  Note: /proc/self/status not accessible.")
        print("  This is NOT a failure. It is a platform limitation.")
        return 0

    delta_mb = delta_kb / 1024.0
    print("  delta:      {:.4f} MB".format(delta_mb))

    if delta_mb < THRESHOLD_MB:
        print("G0.29: CLOSED (delta {:.4f} MB < {:.1f} MB)".format(
            delta_mb, THRESHOLD_MB))
        return 0
    else:
        print("G0.29: FAILED (delta {:.4f} MB >= {:.1f} MB)".format(
            delta_mb, THRESHOLD_MB))
        return 1


if __name__ == "__main__":
    sys.exit(main())
