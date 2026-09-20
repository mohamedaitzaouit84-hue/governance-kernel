# FREEZE — V0.6.1 (Patch)

**Version**: v0.6.1
**Status**: FROZEN
**Date**: 2026-09-20
**Predecessor**: V0.6-CLOSED (5/5 gates, DOI 10.5281/zenodo.22812967)
**Trigger**: J-0.7.1 (found during V0.7.1 Red Team, G0.25 T1)
**Rule**: This document is read before any V0.6.1 code.

---

## 1. Purpose

Fix the single bug discovered in J-0.7.1:

`resolve()` accepts a proposal in `PENDING` state, allowing
bypass of the VOTING phase.

This is a patch release. No new features. No new hypotheses.
No changes to the kernel. Only one file changed.

## 2. Scope Lock

V0.6.1 SHALL modify exactly ONE file:

    agents/multi/consensus.py       (the state check in resolve())

V0.6.1 SHALL NOT modify:

    agents/multi/proposal.py
    agents/multi/communication.py
    agents/multi/coordinator.py
    agents/multi/__init__.py
    (and all kernel files listed in FREEZE_v0.7 section 0)

V0.6.1 SHALL only add:

    tests/gate_v07/test_g025_timing.py   (rebuild — see §5)
    docs/FREEZE_v0.6.1.md                (this file)

## 3. The Fix

In `agents/multi/consensus.py`, `resolve()` currently reads:

    if proposal.state != ProposalState.PENDING and \
       proposal.state != ProposalState.VOTING:
        raise ConsensusError(
            "proposal not votable: state=" + proposal.state
        )

Change to:

    if proposal.state != ProposalState.VOTING:
        raise ConsensusError(
            "proposal not votable: state=" + proposal.state
        )

Rationale: PENDING means "not yet open for voting". Only VOTING
proposals may be resolved. Terminal states (ACCEPTED, REJECTED,
EXECUTED) are also rejected — matching the original intent.

## 4. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| resolve() accepts PENDING | NO |
| resolve() accepts VOTING | YES |
| resolve() accepts SEALED | NO (raise) |
| Other V0.6 tests unchanged | 5/5 pass |
| V0.5 regression | 5/5 pass |
| V0.4 regression | PRI = 1.0000 |
| Kernel files modified | 0 |

## 5. Test Changes

G0.25 test T1 (`t1_vote_before_creation`) is currently
written to expect `ConsensusError` on a PENDING proposal.
After V0.6.1 fix, T1 WILL correctly raise — the test
itself was correct.

However, the test file also needs a small fix: the assertion
message and structure of T1 should be documented as testing
"state check" not "vote timing".

Changes to `test_g025_timing.py`:
- Refactor T1 to use explicit `ProposalState.PENDING`.
- Assert `ConsensusError` is raised.

## 6. Gate

V0.6.1 has ONE gate:

**G0.25-v061** — Timing Safety (patched)
- T1: vote before creation → BLOCKED (ConsensusError)
- T2: vote after sealed → BLOCKED
- T3: rapid fire votes → handled correctly

Pass: 3/3 → G0.25 CLOSED (in V0.6.1 context)
Fail: <3/3 → V0.6.1 FAILED

After V0.6.1, V0.7.1 G0.25 will be re-run.

## 7. Threats to Validity

- This is a patch. No systematic review of other state checks.
- Only the ONE bug found by T1 is fixed.
- If other state-check bugs exist, they are not addressed here.
- Test T1 depends on the fix; it is re-written, not added.

## 8. Success Criteria

V0.6.1 is CLOSED if and only if:

- [ ] One file changed (consensus.py)
- [ ] One line changed (the state check)
- [ ] G0.25 T1 passes (PENDING rejected)
- [ ] G0.25 T2, T3 still pass
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5
- [ ] V0.6 regression: 5/5 (unchanged)
- [ ] J-0.7.1 updated with fix confirmation
- [ ] Commit + tag v0.6.1

## 9. Signature

Status: FROZEN
Version: v0.6.1
Date: 2026-09-20

Immutable after freeze:
1. Scope (one file: consensus.py)
2. The specific line changed
3. G0.25-v061 definition

Editable after freeze:
- Internal test structure (T1 rebuild only)
- JOURNEY.md updates

Rule: One bug, one fix, one test.
Rule: No scope creep.

---
END OF FREEZE v0.6.1
