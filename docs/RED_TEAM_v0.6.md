# Red Team Report — V0.6

**Date**: 2026-09-20
**Phase**: V0.7.1
**Target**: V0.6 (Trust-Weighted Consensus, P-Q12)
**Parent**: docs/FREEZE_v0.7.1_red_team.md
**Result**: 18/18 required attacks handled, 2 known limitations

---

## 1. Executive Summary

V0.6 was attacked with 20 adversarial scenarios across 5 categories.
18 were blocked or handled as expected. 2 are documented limitations
at the protocol layer (S2, S4 — fake-identity detection belongs to
the kernel, not P-Q12).

One real bug was discovered during the red team:

- **J-0.7.1** — resolve() accepted PENDING state
- Fixed in V0.6.1 (one-line patch)
- Verified: T1 now passes, no regressions

The kernel was untouched throughout (G0.ZZ verified).

## 2. What Was Tested

| Category | Scenarios | Test File |
|----------|-----------|-----------|
| Sybil Resistance | 5 | test_g023_sybil.py |
| Collusion Handling | 4 | test_g024_collusion.py |
| Timing Safety | 3 | test_g025_timing.py |
| Trust Bound | 4 | test_g026_trust_manipulation.py |
| Protocol Integrity | 4 | test_g027_protocol_bypass.py |

Total: 20 scenarios across 5 gates.

## 3. Results Per Gate

### G0.23 — Sybil Resistance (H25)
- Passed: 3/5 (S1, S3, S5)
- Not blocked: S2, S4 (known limitations)
- Reason: protocol cannot verify agent identities.
  That is the kernel's job (subject_registry.py).
- Status: CLOSED by "required" criterion
- Recommendation: document that identity verification is the
  kernel's responsibility. Do not weaken P-Q12 for this.

### G0.24 — Collusion Handling (H26)
- Passed: 4/4 (C1, C2, C3, C4)
- Key finding: weight cap (2.0) limits bloc influence.
  A colluding pair cannot exceed 4.0 total weight.
- Status: CLOSED

### G0.25 — Timing Safety (H27)
- Passed: 3/3 (T1, T2, T3) — after fix
- Before fix: T1 failed (2/3)
- Fix: V0.6.1 — resolve() requires VOTING state
- Status: CLOSED (post-fix)

### G0.26 — Trust Bound (H28)
- Passed: 4/4 (M1, M2, M3, M4)
- Covers: huge, negative, wrong type, infinity
- Status: CLOSED

### G0.27 — Protocol Integrity (H29)
- Passed: 4/4 (B1, B2, B3, B4)
- Covers: double resolve, post-execution, quorum, tie
- Status: CLOSED

### G0.ZZ — Kernel Untouched
- 11 files changed since v0.6-closed
- 0 protected files modified
- Only consensus.py modified (v0.6.1 patch)
- Status: CLOSED

## 4. Findings

### Finding J-0.7.1 — resolve() accepts PENDING state

**Severity**: MEDIUM
**Discovered by**: T1 (test_g025_timing.py)
**Logged**: docs/JOURNEY.md (before fix)
**Fixed**: V0.6.1 — one line change
**Verified**: T1 now passes, regressions intact

Full details: docs/JOURNEY.md J-0.7.1

### Known Limitations (not bugs)

**L-1 (S2, S4): Protocol cannot detect fake identities.**
- This is by design.
- Identity verification is in kernel/authorization/subject_registry.py.
- Not a P-Q12 weakness.

## 5. What This Report Does NOT Claim

- V0.6 is NOT cryptographically secure. No formal proof.
- 20 attacks are NOT exhaustive.
- The 5 categories are NOT orthogonal. Overlap exists.
- Self-red-team is NOT equivalent to external red team.
- Passing all gates does NOT mean "no bugs exist".

## 6. Recommendations

1. **Do not weaken P-Q12** for S2/S4. Identity is the kernel's job.
2. **Keep V0.6.1 patch** as the canonical V0.6 for future work.
3. **Future V0.7.x** should add state-machine formalization
   (avoid ad-hoc state checks).
4. **External red team** remains the strongest missing validation.

## 7. Verification

All tests are reproducible:

    cd ~/governance_kernel
    python tests/gate_v07/run_all.py

Expected: 6/6 gates closed, exit 0.

---

**RED TEAM COMPLETE**
**V0.7.1 CLOSED — 6/6 gates**
**Kernel untouched (G0.ZZ verified)**
