# FREEZE — V0.6

**Version**: v0.6.0
**Status**: FROZEN
**Date**: 2026-09-17
**Predecessor**: V0.5-CLOSED (5/5 gates, DOI 10.5281/zenodo.22773365)
**Files**: docs/FREEZE_v0.6.md (this file)
**Rule**: This document is read before any V0.6 code.

---

## 1. Purpose

Test whether the V0.5 kernel can govern multiple cooperating
agents without modifying the kernel.

The kernel is not changed. Cooperation is new. The rules remain.

## 2. Scope (Scope Lock)

IN:
- 3 deterministic agents (FileAgent, ComputeAgent, QueryAgent)
- Cooperative task: Read -> Compute -> Write
- Weighted consensus protocol (trust-based)
- Inter-agent communication through the kernel only
- 8 architectural principles applied (see section 4)
- 3 new hypotheses: H20, H21, H22

OUT:
- No LLM
- No network
- No distributed execution (single device)
- No kernel modifications
- No additional agents
- No multiple consensus protocols

## 3. No Break of Principle

V0.1-V0.5: ZERO external dependencies.
V0.6: ZERO external dependencies (preserved).

No pip install. No C++ toolchain. No model weights.
Python 3.13 standard library only.

## 4. Architectural Principles (8)

These principles guide every V0.6 file. Each has an engineering
name, and each is verifiable by test.

| # | Principle (Arabic) | Engineering Term      | Applied as                         |
|---|--------------------|-----------------------|------------------------------------|
| 1 | التوازن            | Symmetric Balance     | each proposal has a rejection log  |
| 2 | الإحكام            | Structural Integrity  | no agent proposes+votes+executes   |
| 3 | الحدود             | Explicit Boundaries   | every cycle: started, sealed       |
| 4 | الفصل              | Clear Separation      | agents stay in their role          |
| 5 | الشهادة المزدوجة   | Double Attestation    | every decision logged in 2 places  |
| 6 | السنن              | Invariant Laws        | quorum, weight cap, no self-vote   |
| 7 | الميزان            | Weighted Justice      | weight = trust, capped at 2.0      |
| 8 | التقدير            | Prior Estimation      | constants declared before running  |

Inspiration (multiple sources, no hierarchy):
- Constitutional law (checks and balances, quorum)
- Distributed systems (Byzantine fault tolerance, double-ledger)
- ZFS and blockchain (dual attestation)
- Classical texts (structural symmetry)

## 5. Trust-Weighted Consensus (P-Q12)

Weight of an agent's vote = its trust value, capped at MAX_WEIGHT.

Constants (frozen):
- MAX_WEIGHT_PER_AGENT = 2.0
- MIN_QUORUM = 2
- TIE_BREAK = owner signature
- NO_SELF_VOTE = True (an agent cannot vote on its own proposal)

Rules:
1. Proposal requires 1 proposer (any agent with capability).
2. Voting requires MIN_QUORUM voters.
3. Weighted sum decides. Ties broken by owner.
4. Decision is sealed with hash + signature.
5. Every vote is logged with proof.

## 6. Hypotheses Under Test

### H20 — Cooperative Task Success
Statement: 3 agents can complete Read->Compute->Write
without modifying the kernel.
Test: 50 cooperative tasks, deterministic inputs.
Pass: 50/50 tasks complete, 0 kernel modifications.

### H21 — Weighted Consensus Prevents Single-Agent Control
Statement: no single agent can force a decision, even with
maximum trust.
Test: 20 attempts at single-agent control (with max trust 0.85).
Pass: 20/20 rejected by quorum or tie-break rule.

### H22 — Zero-Dependency Preserved
Statement: V0.6 preserves zero-dependency and V0.4 PRI.
Test: rerun V0.4 attack suite + V0.5 gates on V0.6.
Pass: V0.4 PRI = 1.0000 unchanged; V0.5 5/5 gates still closed.

## 7. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Cooperative tasks completed | 50/50 |
| Single-agent control blocked | 20/20 |
| Kernel modifications | 0 |
| V0.4 PRI (regression) | 1.0000 |
| V0.5 gates (regression) | 5/5 |
| Audit chain intact after run | yes |
| Double attestation consistent | 100% |
| No self-vote violation | 0 occurrences |

Thresholds fixed BEFORE running. No post-hoc adjustment.

## 8. Threats to Validity

### Methodological
- One developer, same structural bias as V0.1-V0.5.
- No external red team.
- Cooperative task defined by us (self-referential).
- 50 tasks chosen arbitrarily; not statistically justified.
- 8 principles were declared before code but after design.

### Technical
- Weighted consensus is unproven at scale (only 3 agents).
- Trust values come from V0.5 (already bounded).
- Hash + signature add CPU cost; not yet measured on-device.
- Journal file grows without rotation in V0.6.

### Strategic
- "Multi-agent" is a known field; V0.6 is not first in it.
- No comparison yet with OPA, Cedar, or other governance tools.
- Cannot claim breakthrough; can claim a working demonstration.

## 9. Architecture (Expected)

    governance_kernel/
    ├── agents/
    │   ├── (V0.5 agents unchanged: file_agent.py, compute_agent.py, query_agent.py)
    │   └── multi/
    │       ├── __init__.py
    │       ├── proposal.py         (define Proposal, Rejection)
    │       ├── communication.py    (kernel-mediated channel)
    │       ├── consensus.py        (weighted vote logic)
    │       └── coordinator.py      (Read -> Compute -> Write)
    ├── tests/gate_v06/
    │   ├── test_g018_cooperation.py    (H20)
    │   ├── test_g019_consensus.py      (H21)
    │   ├── test_g020_double_attest.py  (principle 5)
    │   ├── test_g021_v04_regression.py (H22)
    │   ├── test_g022_v05_regression.py (H22)
    │   └── run_all.py
    └── consensus/
        └── journal.jsonl           (second attestation ledger)

NO modifications to:
- kernel/
- authorization/
- policy/
- control/
- audit/
- seed/
- agents/ (V0.5 agents)

The kernel is unchanged. This is H20.

## 10. Proposed Gates (G0.18 - G0.22)

| Gate  | Name                        | Criterion                              |
|-------|-----------------------------|----------------------------------------|
| G0.18 | Cooperative Task Success    | 50/50 tasks complete                   |
| G0.19 | Weighted Consensus Integrity| 20/20 single-agent control blocked     |
| G0.20 | Double Attestation          | 100% decisions in both ledgers         |
| G0.21 | V0.4 Regression             | PRI = 1.0000 unchanged                 |
| G0.22 | V0.5 Regression             | 5/5 gates still closed                 |

Pass rule: 5/5 closed -> V0.6 CLOSED.
4/5 -> V0.6 PARTIAL (V0.6.1).
3 or less -> V0.6 FAILED (document in JOURNEY.md).

## 11. Success Criteria

V0.6 is CLOSED if and only if:

- [ ] G0.18 CLOSED: 50/50 cooperative tasks
- [ ] G0.19 CLOSED: 20/20 single-agent control rejected
- [ ] G0.20 CLOSED: 100% double attestation
- [ ] G0.21 CLOSED: V0.4 PRI unchanged (1.0000)
- [ ] G0.22 CLOSED: V0.5 gates unchanged (5/5)
- [ ] Zero kernel modifications (H20 verified)
- [ ] Audit chain intact after V0.6 runs
- [ ] Public release: GitHub tag v0.6-closed
- [ ] Zenodo DOI for V0.6
- [ ] No external dependencies added

## 12. Signature and Freeze

Status: FROZEN
Version: v0.6.0
Date: 2026-09-17
Reference: FREEZE_v0.6 (rev1)

Immutable after freeze:
1. Number of hypotheses (3: H20, H21, H22)
2. Consensus constants (section 5)
3. Thresholds in section 7
4. Scope Lock in section 2
5. 8 architectural principles (section 4)

Editable after freeze:
- Internal multi-agent code (no interface change)
- Test infrastructure
- Task definitions (must be documented in tests)
- Journal file format

Rule: Failures are logged in JOURNEY.md. Never hidden.

---
END OF FREEZE v0.6
