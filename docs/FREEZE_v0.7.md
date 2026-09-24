# FREEZE — V0.7

**Version**: v0.7.0
**Status**: FROZEN
**Date**: 2026-09-20
**Predecessor**: V0.6-CLOSED (5/5 gates, DOI 10.5281/zenodo.22812967)
**Files**: docs/FREEZE_v0.7.md (this file) + 4 sub-freezes
**Rule**: This document is read before any V0.7 code.

---

## 0. Scope Lock — Kernel Untouched (BINDING)

V0.7 SHALL NOT modify any file in:

    kernel/           (V0.3 separation)
    authorization/    (V0.4/V0.5 governance)
    policy/           (V0.3 signed policy)
    control/          (V0.1 kill switch, resource governor)
    audit/            (V0.1 hash-chained log)
    seed/             (V0.1 trust anchor)
    memory/           (V0.2a episodic + semantic)
    agents/file_agent.py       (V0.5)
    agents/compute_agent.py    (V0.5)
    agents/query_agent.py      (V0.5)
    agents/base_agent.py       (V0.5)
    agents/invariant_checker.py (V0.5)
    agents/trust_manager.py    (V0.5)
    agents/governed_action_v05.py (V0.5)
    agents/register_agents.py  (V0.5)
    agents/multi/__init__.py       (V0.6)
    agents/multi/proposal.py       (V0.6)
    agents/multi/consensus.py      (V0.6)
    agents/multi/communication.py  (V0.6)
    agents/multi/coordinator.py    (V0.6)

V0.7 SHALL only add:

    agents/multi/red_team/         (V0.7.1)
    agents/multi/benchmark/        (V0.7.2)
    agents/multi/coordinator_v2.py (V0.7.3)
    agents/multi/delegation.py     (V0.7.4)
    tests/gate_v07/                (all)
    docs/FREEZE_v0.7*.md
    docs/RED_TEAM_v0.6.md
    docs/PERFORMANCE_v0.6.md
    docs/GATES_v0.7_report.md

**v0.7.15 exception (J-0.8.28)**:
    authorization/subjects.json  (additive only — bootstrap.py adds
    default subjects; see docs/FREEZE_v0.7.15.md)

**Any change to a kernel file → V0.7 FAILED automatically.**

**Verification**: `tests/gate_v07/test_g0ZZ_kernel_untouched.py`
computes `git diff --name-only v0.6-closed HEAD` and fails if any
file matches the protected list above.

## 1. Purpose

Extend V0.6 with four independent improvements, without modifying
the kernel or any V0.5/V0.6 file.

Each improvement is a self-contained phase with its own freeze,
gates, and tests. Phases run in order. A phase that fails does
not block earlier phases.

## 2. Structure

V0.7 = 4 sequential phases, 1 DOI, 15 gates.

    V0.7.1 — Red Team (20 attacks, 5 gates)         [G0.23 - G0.27]
    V0.7.2 — Performance (measurements, 3 gates)    [G0.28 - G0.30]
    V0.7.3 — Real Agents (V0.5 integration, 4 gates)[G0.31 - G0.34]
    V0.7.4 — Delegation (new pattern P-Q13, 3 gates)[G0.35 - G0.37]

Each phase: its own FREEZE, its own tests, its own commit,
and a tag (v0.7.1, v0.7.2, v0.7.3, v0.7.4).

Final tag: v0.7-closed.

## 3. Order and Rationale

Order: V0.7.1 → V0.7.2 → V0.7.3 → V0.7.4

Rationale:
- V0.7.1 (Red Team) audits V0.6 BEFORE adding features.
- V0.7.2 (Performance) measures V0.6 BEFORE integration.
- V0.7.3 (Real Agents) integrates AFTER audit and measurement.
- V0.7.4 (Delegation) adds new pattern LAST, on solid ground.

Rule: no phase starts before the previous one is CLOSED.

## 4. Kernel Protection Across Phases

At every phase:

- Zero modifications to protected files (section 0).
- All new tests import from `agents/multi/` (V0.6) without editing.
- All V0.4/V0.5/V0.6 regression suites must pass unchanged.
- `test_g0ZZ_kernel_untouched.py` must pass.

## 5. Pre-registered Thresholds (V0.7 overall)

| Threshold | Target |
|-----------|--------|
| Phases completed | 4/4 |
| Total gates closed | 15/15 |
| Kernel modifications | 0 |
| V0.4 PRI (regression) | 1.0000 |
| V0.5 gates (regression) | 5/5 |
| V0.6 gates (regression) | 5/5 |
| New external dependencies | 0 |
| Every number in report sourced | 100% |

## 6. Phase Overviews

Each phase is defined in detail in its own sub-freeze file.
Summary here.

### V0.7.1 — Red Team
- File: docs/FREEZE_v0.7.1_red_team.md
- Attacks: 20 across 5 categories (Sybil, Collusion, Timing,
  Trust Manipulation, Protocol Bypass)
- Gates: G0.23 - G0.27 (5 gates)
- Deliverable: docs/RED_TEAM_v0.6.md
- Constraint: No changes to V0.6 or V0.5 files

### V0.7.2 — Performance
- File: docs/FREEZE_v0.7.2_performance.md
- Measurements: cycle time, consensus time, memory,
  throughput, baseline comparison
- Gates: G0.28 - G0.30 (3 gates)
- Deliverable: docs/PERFORMANCE_v0.6.md
- Constraint: Measurement only, no code changes

### V0.7.3 — Real Agents
- File: docs/FREEZE_v0.7.3_real_agents.md
- Integration: V0.5 FileAgent, ComputeAgent, QueryAgent
  coordinated by V0.6 protocol
- Gates: G0.31 - G0.34 (4 gates)
- Deliverable: agents/multi/coordinator_v2.py
- New hypothesis: H23 (real agents coordinated without modification)
- Constraint: V0.5 agents untouched

### V0.7.4 — Delegation
- File: docs/FREEZE_v0.7.4_delegation.md
- New pattern: P-Q13 (Delegated Authority)
- Gates: G0.35 - G0.37 (3 gates)
- Deliverable: agents/multi/delegation.py + P-Q13 in PATTERNS.md
- New hypothesis: H24 (delegation revocable mid-flight)
- Constraint: Delegation is an additive layer, never touches kernel

## 7. Threats to Validity (V0.7 overall)

### Methodological
- Single developer, same structural bias as V0.1 - V0.6.
- No external red team (V0.7.1 is self-red-team).
- Cooperative tasks defined by us.
- Performance measured on one device only.
- Delegation pattern designed without comparison to OPA/Cedar
  delegation models.

### Technical
- Measurements on Termux/Android may not generalize to
  production hardware.
- Journal file grows without rotation (still true in V0.7).
- Weighted consensus tested at 3 agents (not 10+).
- No multi-run statistical analysis planned.

### Strategic
- Kernel untouched (H20/H22 preserved) means V0.7 cannot
  improve performance by modifying the kernel.
- All improvements are additive. This limits speedups.
- "Multi-agent" is a known field; V0.7 is not first.
- No user feedback loop. All tests are self-authored.

## 8. Success Criteria

V0.7 is CLOSED if and only if:

- [ ] V0.7.1 CLOSED (5/5 gates)
- [ ] V0.7.2 CLOSED (3/3 gates)
- [ ] V0.7.3 CLOSED (4/4 gates)
- [ ] V0.7.4 CLOSED (3/3 gates)
- [ ] Total: 15/15 gates closed
- [ ] Kernel untouched (test_g0ZZ passes)
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5 unchanged
- [ ] V0.6 regression: 5/5 unchanged
- [ ] Zero external dependencies
- [ ] Every number in GATES_v0.7_report.md has a source file
- [ ] All findings logged in JOURNEY.md BEFORE fixes
- [ ] Public release: tag v0.7-closed
- [ ] Zenodo DOI for V0.7
- [ ] README + AUTHORS updated with V0.7 DOI

## 9. Signature and Freeze

Status: FROZEN
Version: v0.7.0
Date: 2026-09-20
Reference: FREEZE_v0.7 (rev1)

Immutable after freeze:
1. Kernel Untouched rule (section 0)
2. Number of phases (4)
3. Total gates (15)
4. Order of phases (V0.7.1 -> V0.7.4)
5. Thresholds in section 5
6. Any item in section 8 (Success Criteria)

Editable after freeze:
- Internal phase tests (no interface change)
- Test infrastructure
- Task definitions (must be documented in tests)
- Additional findings logged in JOURNEY.md

Rule: Failures are logged in JOURNEY.md. Never hidden.
Rule: Kernel is untouched. Always verified.

---
END OF FREEZE v0.7
