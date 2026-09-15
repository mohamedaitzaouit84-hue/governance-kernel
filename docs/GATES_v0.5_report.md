# V0.5 — Final Gate Report

**Version**: v0.5.0
**Status**: CLOSED
**Date**: 2026-09-15
**Predecessor**: V0.4-CLOSED (Kernel PRI = 1.0000)
**Freeze reference**: docs/FREEZE_v0.5.md

---

## 1. Verdict

    V0.5 CLOSED — 5/5 gates
    exit code 0

All pre-registered gates (G0.13 - G0.17) passed.
No threshold was adjusted. No gate was skipped.

## 2. Gate Results

| Gate  | Name                   | Result | Score |
|-------|------------------------|--------|-------|
| G0.13 | Agent Registration     | CLOSED | 3/3   |
| G0.14 | Governed Execution     | CLOSED | 5/5   |
| G0.15 | Trust Dynamics         | CLOSED | 6/6   |
| G0.16 | Invariant Enforcement  | CLOSED | 10/10 |
| G0.17 | Kill Switch Respect    | CLOSED | 6/6   |

Total: 30/30 checks passed.

## 3. Hypotheses Status

| Hyp | Name                    | Status  | Evidence |
|-----|-------------------------|---------|----------|
| H1  | Dynamic Trust           | TESTED  | G0.15: 6/6 |
| H13 | Progressive Capability  | TESTED  | see §5 |
| H14 | Base Invariants         | TESTED  | G0.16: 10/10 |
| H16 | Policy Extension        | TESTED  | V0.4 regression PRI = 1.0000 |

## 4. H16 — Empirical Proof (Policy Extension)

After adding V0.5 artifacts (P-Q11, 3 agents, 3 subjects,
governed_action_v05), V0.4 attack suite was re-run.

Result:

    Baseline-A (no gate)     0/54   PRI = 0.0000
    Baseline-B (Whitelist)   41/54  PRI = 0.7593
    Kernel                   54/54  PRI = 1.0000

Verdict: Kernel PRI = 1.0000  (threshold 0.95)
--> V0.4 CLOSED (unchanged)

Conclusion: P-Q11 does NOT alter any V0.1-V0.4 behavior.
Adding N new roles via extension preserves all legacy roles.

## 5. H13 — Progressive Capability

Agents start with tier-1 capabilities at trust 0.10.
- FileAgent:    file_read, file_list
- ComputeAgent: compute_add, compute_sub
- QueryAgent:   query_lookup, query_count

At trust >= 0.30 (tier 2):
- FileAgent:    + file_write
- ComputeAgent: + compute_mul
- QueryAgent:   + query_verify

At trust >= 0.60 (tier 3):
- FileAgent:    + file_delete
- ComputeAgent: + compute_div
- QueryAgent:   (unchanged, read-only by design)

Verified via current_capabilities() at multiple trust levels.

## 6. Architecture Delivered

### New files

    agents/
      __init__.py
      base_agent.py              (205 lines)
      trust_manager.py           (81 lines)
      invariant_checker.py       (87 lines)
      file_agent.py              (23 lines)
      compute_agent.py           (23 lines)
      query_agent.py             (23 lines)
      register_agents.py         (110 lines)
      governed_action_v05.py     (88 lines)

    authorization/
      policy_extension.py        (77 lines)
      v05_gate.py                (50 lines)

    policy/policies/
      v0.5_agents.yaml           (37 lines)

    tests/gate_v05/
      __init__.py                (1 line)
      test_g013_registration.py  (60 lines)
      test_g014_governed.py      (65 lines)
      test_g015_trust.py         (59 lines)
      test_g016_invariants.py    (80 lines)
      test_g017_killswitch.py    (81 lines)
      run_all.py                 (47 lines)

### Modified (V0.5 scope only)

    authorization/subjects.json  (+3 subjects, 0 removed)
    agents/base_agent.py         (import v05 + subject_id)

### NOT modified (Scope Lock respected)

    policy/policies/default.yaml       (untouched, signature valid)
    policy/policy_engine.py            (untouched)
    policy/policy_store.py             (untouched)
    authorization/permission_gate.py   (untouched)
    authorization/governed_action.py   (untouched)
    control/kill_switch.py             (untouched)
    seed/root.py                       (untouched)
    audit/*                            (untouched)

## 7. New Patterns Documented

- P-Q11 — Policy Extension (Layered Permissions)
  See docs/PATTERNS.md

## 8. Threats to Validity

- Deterministic agents only (no real LLM)
- 20 scenarios, 200 ops target (this run: 30 checks)
- Same developer wrote tests and code (structural bias)
- No external red team
- Kill switch clear path requires owner signature (verified)

## 9. Inventory (Cumulative)

| Item | V0.4 | V0.5 |
|------|------|------|
| Commits | ~30 | ~40 |
| Lines of code | ~2500 | ~3200 |
| Reference docs | 17 | 20 |
| Patterns | 15 | 16 (+P-Q11) |
| Gates closed | V0.1-V0.4 | +V0.5 |
| Test suites | 2 (v03, v04) | +1 (v05) |

## 10. Next

Option A: publish V0.4 on GitHub public + LICENSE + SECURITY.md
Option B: start V0.6 (local LLM)
Option C: bug bounty tiny scoped to V0.4

---

**FROZEN — 2026-09-15**
**V0.5 CLOSED — 5/5 gates**
