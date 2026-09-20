"""G0.28 — Cycle Time (H30).

Criterion: full Read -> Compute -> Write cycle median < 100 ms.

Method: 100 cycles measured via time.perf_counter().
Warm-up: 3 cycles.
Result: median reported (not mean).

Read-only. Does not modify V0.6 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.benchmark.runner import (
    measure_cycle_time,
    DEFAULT_TRUSTS,
)

THRESHOLD_MS = 100.0
N_SAMPLES = 100


def main():
    print("  Measuring {} cycles (perf_counter)...".format(N_SAMPLES))
    r = measure_cycle_time(N_SAMPLES, DEFAULT_TRUSTS)

    median_ms = r["median"] * 1000.0
    min_ms = r["min"] * 1000.0
    max_ms = r["max"] * 1000.0
    std_ms = r["std"] * 1000.0

    print("  n:      {}".format(r["n"]))
    print("  median: {:.4f} ms".format(median_ms))
    print("  min:    {:.4f} ms".format(min_ms))
    print("  max:    {:.4f} ms".format(max_ms))
    print("  std:    {:.4f} ms".format(std_ms))
    print("  threshold: < {:.1f} ms".format(THRESHOLD_MS))

    if median_ms < THRESHOLD_MS:
        print("G0.28: CLOSED (median {:.4f} ms < {:.1f} ms)".format(
            median_ms, THRESHOLD_MS))
        return 0
    else:
        print("G0.28: FAILED (median {:.4f} ms >= {:.1f} ms)".format(
            median_ms, THRESHOLD_MS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
