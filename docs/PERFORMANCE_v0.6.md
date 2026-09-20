# Performance Report — V0.6

**Date**: 2026-09-20
**Phase**: V0.7.2
**Target**: V0.6 (Trust-Weighted Consensus, P-Q12)
**Device**: Android phone, Termux
**Python**: 3.13
**Parent**: docs/FREEZE_v0.7.2_performance.md
**Result**: 3/3 gates closed

---

## 1. Executive Summary

V0.6 was measured with `time.perf_counter()` and RSS sampling.
100 samples for cycle time, 1000 cycles for memory, 10 runs of
100 for throughput.

All three pre-registered thresholds were met by wide margins.
Numbers vary between runs (see section 5 — Honesty about
variance), but the gap to thresholds is large (11× to 120×).

## 2. What Was Measured

| Metric | Method | Sample size |
|--------|--------|-------------|
| Cycle time | perf_counter, 100 samples | 100 |
| Consensus time | perf_counter, 100 samples | 100 (informational) |
| Memory delta | RSS delta, 1000 cycles | 1 run |
| Throughput | perf_counter, 10x100 cycles | 10 |

Baseline: proposal operations WITHOUT resolve(), same process.

## 3. Results (V0.7.2 run)

### G0.28 — Cycle Time
- median: **1.1125 ms**
- min:    1.0920 ms
- max:    3.9636 ms
- std:    0.3308 ms
- threshold: < 100.0 ms
- **Result**: CLOSED (89× margin)

### G0.29 — Memory Bound
- rss before: 24840 kB
- rss after:  24364 kB
- delta:      **-0.4648 MB**
- threshold:  < 50.0 MB
- **Result**: CLOSED (no growth observed)

### G0.30 — Throughput
- median: **897.29 cycles/sec**
- min:    883.44 cycles/sec
- max:    899.43 cycles/sec
- std:    4.56 cycles/sec
- threshold: > 100.0 cycles/sec
- **Result**: CLOSED (8.9× margin)

## 4. Source of Every Number

| Number | Source file | Line |
|--------|-------------|------|
| Cycle median (ms) | tests/gate_v07/test_g028_cycle_time.py | main() |
| Memory delta (MB) | tests/gate_v07/test_g029_memory.py | main() |
| Throughput median (cycles/sec) | tests/gate_v07/test_g030_throughput.py | main() |

To reproduce:

    cd ~/governance_kernel
    python tests/gate_v07/test_g028_cycle_time.py
    python tests/gate_v07/test_g029_memory.py
    python tests/gate_v07/test_g030_throughput.py

## 5. Honesty about Variance

Numbers varied between two runs on the same device:

| Metric | Run 1 | Run 2 | Delta |
|--------|-------|-------|-------|
| Cycle median | 0.833 ms | 1.112 ms | +34% |
| Throughput median | 1131/s | 897/s | -21% |

Possible causes:
- Android background processes
- CPU thermal state (phone warm/cold)
- Python GC timing
- Screen state (on/off affects CPU governor)

**Interpretation**: variance is real. Numbers are NOT stable.
The thresholds are far enough (11-120×) that variance does not
change the CLOSED/FAILED outcome. But absolute numbers should
NOT be quoted as if they were stable.

## 6. What This Report Does NOT Claim

- **Not a benchmark vs OPA/Cedar.** No comparison performed.
- **Not "fast" or "slow".** These words require reference points.
- **Not production-ready.** No load testing, no multi-threading.
- **Not generalizable.** Single device, single Python version.
- **Not a security claim.** Performance is orthogonal to security.

## 7. Threats to Validity

- Single device (Android/Termux).
- No thermal control.
- RSS approximate on Android.
- GC pauses not excluded.
- Baseline uses same process (contention possible).
- Only medians reported; tail latencies not measured.

## 8. Recommendation

1. V0.6 protocol is **computationally cheap**. It is NOT the
   bottleneck in a real workflow.
2. The bottleneck in any real use will be the agent's own work
   (file I/O, network, LLM inference), NOT the governance.
3. For production, re-measure on target hardware. This report
   is a **reference, not a contract**.
4. Consider adding tail-latency (p95, p99) measurement in a
   future phase. Medians hide rare slow paths.

## 9. Verification

All numbers are reproducible from the test files.

    cd ~/governance_kernel
    python tests/gate_v07/run_all.py

Expected: 9/9 gates closed, exit 0.

---

**PERFORMANCE COMPLETE**
**V0.7.2 CLOSED — 3/3 gates**
**Kernel untouched (G0.ZZ verified)**
