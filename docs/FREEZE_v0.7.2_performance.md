# FREEZE — V0.7.2 (Performance)

**Version**: v0.7.2
**Status**: FROZEN
**Date**: 2026-09-20
**Parent**: docs/FREEZE_v0.7.md
**Scope**: Measure V0.6 performance with real numbers
**Rule**: This document is read before any V0.7.2 code.

---

## 1. Purpose

Measure V0.6 (Trust-Weighted Consensus, P-Q12) and the V0.6
coordinator. Produce real numbers, not estimates.

No new features. No changes to V0.6 files. Measurement only.

The output is not "V0.6 is fast". The output is:
"On this specific device, in this specific Python version,
the following numbers were observed, with these caveats."

## 2. Scope Lock

V0.7.2 SHALL NOT modify:

    agents/multi/proposal.py       (V0.6)
    agents/multi/consensus.py      (V0.6, patched as V0.6.1)
    agents/multi/communication.py  (V0.6)
    agents/multi/coordinator.py    (V0.6)
    (and all kernel files listed in FREEZE_v0.7 section 0)

V0.7.2 SHALL only add:

    agents/multi/benchmark/__init__.py
    agents/multi/benchmark/runner.py     (measurement harness)
    tests/gate_v07/test_g028_cycle_time.py
    tests/gate_v07/test_g029_memory.py
    tests/gate_v07/test_g030_throughput.py
    docs/PERFORMANCE_v0.6.md

## 3. Measurement Policy

All timing uses `time.perf_counter()` (monotonic, high-resolution).
Wall clock (`time.time()`) is NOT used for measurement.

Sample sizes:
- Cycle time: 100 runs
- Consensus time: 100 runs
- Throughput: 10 runs of 100 tasks each
- Memory: 1 run of 1000 cycles

Warm-up: 3 runs before measurement (JIT, cache effects).
Result reported: median (not mean) + min + max + std.

Rationale for median: robust to outliers on Android.

## 4. Baseline Definition

**Baseline** = same proposal operations WITHOUT resolve() call.
This isolates protocol cost (weighted_vote + resolve) from
proposal creation cost.

Baseline measured in the same process, same warm-up, same
sample size. This controls for environment variance.

## 5. Hypotheses (new)

### H30 — Cycle Time Bound
Statement: a full Read -> Compute -> Write cycle completes
in under 100 milliseconds (median) on this device.
Test: 100 cycles measured.
Pass: median < 100ms.

### H31 — Memory Bound
Statement: 1000 cycles consume under 50 MB of additional
memory (measured via RSS delta).
Test: 1 run of 1000 cycles, measure RSS before/after.
Pass: delta < 50MB.

### H32 — Throughput
Statement: V0.6 protocol achieves over 100 decisions per
second (median) at 3 agents.
Test: 10 runs of 100 decisions each.
Pass: median > 100 decisions/sec.

## 6. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Cycle time median | < 100 ms |
| Consensus time median | < 5 ms |
| Memory delta (1000 cycles) | < 50 MB |
| Throughput median | > 100 decisions/sec |
| Kernel files modified | 0 |
| V0.6 files modified | 0 |
| Tests depend on external libs | 0 |

Thresholds are fixed BEFORE running. No post-hoc adjustment.

## 7. Proposed Gates (G0.28 - G0.30)

| Gate  | Name          | Criterion |
|-------|---------------|-----------|
| G0.28 | Cycle Time    | median < 100 ms over 100 runs |
| G0.29 | Memory Bound  | delta < 50 MB over 1000 cycles |
| G0.30 | Throughput    | median > 100 decisions/sec |

Pass rule: 3/3 closed -> V0.7.2 CLOSED.
2/3 -> V0.7.2 PARTIAL (findings logged, V0.7.2.1 if needed).
1 or less -> V0.7.2 FAILED (JOURNEY.md entry).

## 8. Threats to Validity

### Methodological
- Single device (Android/Termux). Results do not generalize.
- Single Python version (3.13).
- Android thermal throttling not controlled.
- Background processes not controlled.
- Median chosen; mean may differ under load.

### Technical
- perf_counter() resolution is OS-dependent.
- RSS measurement approximate on Android.
- Python GC pauses not excluded from measurements.
- Multi-threading not tested (V0.6 is single-threaded).

### Strategic
- Numbers are NOT benchmarks vs OPA/Cedar.
- "Fast" or "slow" claims require comparison, not provided here.
- Measurement does not imply production readiness.

## 9. Success Criteria

V0.7.2 is CLOSED if and only if:

- [ ] G0.28 CLOSED: cycle time median < 100 ms
- [ ] G0.29 CLOSED: memory delta < 50 MB
- [ ] G0.30 CLOSED: throughput > 100 decisions/sec
- [ ] Zero kernel modifications
- [ ] Zero V0.6 file modifications
- [ ] test_g0ZZ_kernel_untouched.py still passes
- [ ] V0.4/V0.5/V0.6 regressions pass
- [ ] docs/PERFORMANCE_v0.6.md written with sourced numbers
- [ ] Commit + tag v0.7.2

## 10. Signature

Status: FROZEN
Version: v0.7.2
Date: 2026-09-20
Reference: FREEZE_v0.7.2 (rev1)

Immutable after freeze:
1. Measurement method (perf_counter)
2. Baseline definition (no resolve)
3. Thresholds in section 6
4. Gate definitions in section 7
5. Scope (measurement only)

Editable after freeze:
- Test infrastructure
- Number formatting in report
- Additional caveats to Threats

Rule: Numbers must be reproducible.
Rule: Kernel untouched.

---
END OF FREEZE v0.7.2
