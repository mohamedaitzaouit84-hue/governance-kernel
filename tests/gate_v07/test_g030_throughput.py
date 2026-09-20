"""G0.30 — Throughput (H32).

Criterion: median > 100 decisions/sec over 10 runs of 100 cycles.

Method: 10 runs of 100 cycles. Rate = 100 / elapsed.
Result: median rate reported.

Read-only. Does not modify V0.6 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.benchmark.runner import (
    measure_throughput,
    DEFAULT_TRUSTS,
)

THRESHOLD_RATE = 100.0
N_RUNS = 10
BATCH_SIZE = 100


def main():
    print("  Measuring throughput: {} runs x {} cycles...".format(
        N_RUNS, BATCH_SIZE))
    r = measure_throughput(N_RUNS, BATCH_SIZE, DEFAULT_TRUSTS)

    median_rate = r["median"]
    min_rate = r["min"]
    max_rate = r["max"]
    std_rate = r["std"]

    print("  n:      {}".format(r["n"]))
    print("  median: {:.2f} cycles/sec".format(median_rate))
    print("  min:    {:.2f} cycles/sec".format(min_rate))
    print("  max:    {:.2f} cycles/sec".format(max_rate))
    print("  std:    {:.2f} cycles/sec".format(std_rate))
    print("  threshold: > {:.1f} cycles/sec".format(THRESHOLD_RATE))

    if median_rate > THRESHOLD_RATE:
        print("G0.30: CLOSED (median {:.2f} > {:.1f})".format(
            median_rate, THRESHOLD_RATE))
        return 0
    else:
        print("G0.30: FAILED (median {:.2f} <= {:.1f})".format(
            median_rate, THRESHOLD_RATE))
        return 1


if __name__ == "__main__":
    sys.exit(main())
