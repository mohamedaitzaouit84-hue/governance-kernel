# FREEZE — V0.7.1 (Red Team)

**Version**: v0.7.1
**Status**: FROZEN
**Date**: 2026-09-20
**Parent**: docs/FREEZE_v0.7.md
**Scope**: Adversarial testing of V0.6 consensus (P-Q12)
**Rule**: This document is read before any V0.7.1 code.

---

## 1. Purpose

Audit V0.6 (Trust-Weighted Consensus, P-Q12) with 20 adversarial
attempts across 5 categories. No new features. Only attacks.

Any successful attack is a real finding, logged in JOURNEY.md
BEFORE any fix. Any unsuccessful attack confirms current defenses.

The output is not "V0.6 is secure". The output is:
"20 specific attacks were attempted, with N blocked and M findings".

## 2. Scope Lock

V0.7.1 SHALL NOT modify:

    agents/multi/proposal.py       (V0.6)
    agents/multi/consensus.py      (V0.6)
    agents/multi/communication.py  (V0.6)
    agents/multi/coordinator.py    (V0.6)
    (and all kernel files listed in FREEZE_v0.7 section 0)

V0.7.1 SHALL only add:

    tests/gate_v07/__init__.py
    tests/gate_v07/test_g023_sybil.py
    tests/gate_v07/test_g024_collusion.py
    tests/gate_v07/test_g025_timing.py
    tests/gate_v07/test_g026_trust_manipulation.py
    tests/gate_v07/test_g027_protocol_bypass.py
    tests/gate_v07/test_g0ZZ_kernel_untouched.py
    tests/gate_v07/run_all.py
    docs/RED_TEAM_v0.6.md
    docs/JOURNEY.md (append only, for findings)

## 3. Attack Categories (20 attempts total)

### Category 1 — Sybil Attacks (5 attempts)
An attacker creates fake identities to gain extra votes.

| # | Attack | Expected |
|---|--------|----------|
| S1 | Same agent_id voted twice in one proposal | BLOCKED (J-0.6.1 fix) |
| S2 | Fake agent_id not in registry | BLOCKED (quorum) |
| S3 | Two proposals, same agent, different payloads | INDEPENDENT decisions |
| S4 | 100 votes with rotating fake ids | BLOCKED (all rejected) |
| S5 | Single real agent + 3 fake ids | BLOCKED (only 1 real vote) |

### Category 2 — Collusion Attacks (4 attempts)
Multiple legitimate agents coordinate to force an outcome.

| # | Attack | Expected |
|---|--------|----------|
| C1 | 2 agents always vote same way (bloc) | Decision weighted, no bypass |
| C2 | 3 agents bypass proposer self-vote rule | Self-vote still blocked |
| C3 | Trust inflation before vote | Weight still capped at 2.0 |
| C4 | Colluding voters exceed quorum safely | Detected via outlier pattern |

### Category 3 — Timing Attacks (3 attempts)
Exploit temporal aspects of consensus.

| # | Attack | Expected |
|---|--------|----------|
| T1 | Vote before proposal is created | BLOCKED (state check) |
| T2 | Vote after proposal is sealed | BLOCKED (is_final check) |
| T3 | Rapid-fire votes in single cycle | All recorded, quorum enforced |

### Category 4 — Trust Manipulation (4 attempts)
Exploit trust value semantics.

| # | Attack | Expected |
|---|--------|----------|
| M1 | trust = 10.0 | Capped at MAX_WEIGHT_PER_AGENT (2.0) |
| M2 | trust = -1.0 | BLOCKED (negative trust) |
| M3 | trust = NaN (if possible) | BLOCKED (invalid type) |
| M4 | trust = infinity | Capped at 2.0 |

### Category 5 — Protocol Bypass (4 attempts)
Attempt to bypass consensus protocol rules.

| # | Attack | Expected |
|---|--------|----------|
| B1 | resolve() called twice on same proposal | BLOCKED (state check) |
| B2 | Vote on already-executed proposal | BLOCKED (is_final) |
| B3 | Missing MIN_QUORUM with high trust | REJECTED |
| B4 | Tie broken without owner signature | REJECTED |

## 4. Hypotheses (new)

### H25 — Sybil Resistance
Statement: No combination of fake agent_ids can force a
proposal to ACCEPTED without at least MIN_QUORUM real
distinct votes.
Test: Sybil attacks S1-S5.
Pass: 5/5 blocked.

### H26 — Collusion Detection
Statement: Two colluding real agents cannot force ACCEPTED
when a third independent agent rejects with equal weight.
Test: Collusion attacks C1-C4.
Pass: 4/4 handled correctly (blocked or neutrally weighted).

### H27 — Timing Safety
Statement: Votes cast outside the proposal's lifetime
(before creation or after sealing) are rejected.
Test: Timing attacks T1-T3.
Pass: 3/3 rejected.

### H28 — Trust Bound
Statement: No trust value (NaN, infinity, negative, huge)
can produce a vote weight outside [0, MAX_WEIGHT_PER_AGENT].
Test: Trust manipulation attacks M1-M4.
Pass: 4/4 blocked or capped.

### H29 — Protocol Integrity
Statement: resolve() and vote() cannot bypass state rules.
Test: Protocol bypass attacks B1-B4.
Pass: 4/4 rejected.

## 5. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Total attacks | 20 |
| Blocked | 20 |
| Findings logged | as needed |
| Kernel modifications | 0 |
| V0.6 files modified | 0 |
| Regression V0.6 suite | 5/5 pass |

Thresholds are fixed BEFORE running. No post-hoc adjustment.

## 6. Proposed Gates (G0.23 - G0.27)

| Gate  | Name                    | Criterion |
|-------|-------------------------|-----------|
| G0.23 | Sybil Resistance        | 5/5 attacks blocked |
| G0.24 | Collusion Handling      | 4/4 attacks handled |
| G0.25 | Timing Safety           | 3/3 attacks rejected |
| G0.26 | Trust Bound             | 4/4 attacks blocked or capped |
| G0.27 | Protocol Integrity      | 4/4 attacks rejected |

Pass rule: 5/5 closed -> V0.7.1 CLOSED.
4/5 -> V0.7.1 PARTIAL (findings logged, V0.7.1.1 to follow).
3 or less -> V0.7.1 FAILED (JOURNEY.md entry + V0.6.1 emergency).

## 7. Threats to Validity

- Self-red-team (same author as V0.6). Structural bias.
- 20 attacks chosen by author. Not exhaustive.
- Attack categories are conceptual, not formal.
- No cryptographic proof of security. Only behavioral tests.
- Time attacks assume single-threaded execution.

## 8. Success Criteria

V0.7.1 is CLOSED if and only if:

- [ ] All 5 gates (G0.23 - G0.27) closed
- [ ] 20/20 attacks blocked or handled
- [ ] Zero kernel modifications
- [ ] Zero V0.6 file modifications
- [ ] test_g0ZZ_kernel_untouched.py passes
- [ ] V0.6 regression suite passes (5/5)
- [ ] All findings logged in JOURNEY.md
- [ ] docs/RED_TEAM_v0.6.md written
- [ ] Commit + tag v0.7.1

## 9. Signature

Status: FROZEN
Version: v0.7.1
Date: 2026-09-20
Reference: FREEZE_v0.7.1 (rev1)

Rule: Findings logged before fixes.
Rule: Kernel untouched.

---
END OF FREEZE v0.7.1
