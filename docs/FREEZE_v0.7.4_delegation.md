# FREEZE — V0.7.4 (Delegation)

**Version**: v0.7.4
**Status**: FROZEN
**Date**: 2026-09-22
**Parent**: docs/FREEZE_v0.7.md
**Scope**: Add P-Q13 (Delegated Authority) as a new pattern
**Rule**: This document is read before any V0.7.4 code.

---

## 1. Purpose

Add a new architectural pattern to the system: Delegated Authority
(P-Q13). The owner can grant a temporary, scope-bound authority
to an agent. The delegation can expire (by time) or be revoked
(by the owner) mid-flight.

This is the last phase of V0.7. No kernel modifications.

## 2. Scope Lock

V0.7.4 SHALL NOT modify:

    agents/file_agent.py, compute_agent.py, query_agent.py
    agents/base_agent.py, invariant_checker.py, trust_manager.py
    agents/governed_action_v05.py, register_agents.py
    agents/multi/__init__.py, proposal.py, consensus.py,
                 communication.py, coordinator.py, coordinator_v2.py
    authorization/*, policy/*, control/*, audit/*, seed/*

V0.7.4 SHALL only add:

    agents/multi/delegation.py
    tests/gate_v07/test_g035_delegation_issued.py
    tests/gate_v07/test_g036_delegation_expires.py
    tests/gate_v07/test_g037_delegation_revoked.py
    docs/FREEZE_v0.7.4_delegation.md (this file)
    docs/PATTERNS.md (add P-Q13 entry)

## 3. Pattern P-Q13 — Delegated Authority

Definition: a scoped, time-bound, revocable grant of authority
from the owner to an agent.

Fields:
  - delegation_id      unique identifier
  - granter_id         who granted (usually "owner")
  - grantee_id         agent id (e.g. "file_agent_1")
  - scope              list of allowed actions
  - issued_at          unix timestamp
  - expires_at         unix timestamp
  - revoked_at         None or unix timestamp
  - commitment         hash of the above (immutability)

Rules:
  1. A delegation is valid if now < expires_at AND revoked_at is None.
  2. Scope matching: action must be in the delegation's scope list.
  3. Revocation: immediate effect, but does NOT alter proposals
     already accepted before revocation.
  4. No delegation can grant "owner" scope to an agent.
  5. Delegations are kept in memory (V0.7.4). Persistence is V0.7.4.1.

## 4. Hypotheses Under Test

### H24 — Delegation Revocable Mid-Flight

Statement: A delegation can be revoked after being issued, and
the revocation does NOT alter proposals already accepted.

Test: issue delegation, run a proposal (ACCEPTED), revoke,
run another proposal (must be denied by scope check).

Pass: 5/5 attempts to use revoked delegation are blocked.

## 5. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Delegations issued | 5/5 |
| Delegations expiring | 5/5 |
| Delegations revoked | 5/5 |
| Attempts on revoked delegation | 0 allowed |
| Kernel files modified | 0 |
| V0.5/V0.6 files modified | 0 |

Thresholds fixed BEFORE running. No post-hoc adjustment.

## 6. Proposed Gates (G0.35 - G0.37)

| Gate  | Name                | Criterion |
|-------|---------------------|-----------|
| G0.35 | Delegation Issued   | 5/5 valid delegations |
| G0.36 | Delegation Expires  | 5/5 expired delegations denied |
| G0.37 | Delegation Revoked  | 5/5 revoked delegations denied |

Pass rule: 3/3 -> V0.7.4 CLOSED.
2/3 -> V0.7.4 PARTIAL.
1 or less -> V0.7.4 FAILED (JOURNEY.md entry).

## 7. Threats to Validity

- In-memory only: delegations do not survive restart.
- No persistence layer: not production-grade.
- Single-device test: no distributed delegation.
- No comparison to existing delegation models
  (e.g. OAuth scopes, AWS IAM temporary credentials).
- H24 tests revocation mid-flight at protocol level,
  not at kernel level.

## 8. Success Criteria

V0.7.4 is CLOSED if and only if:

- [ ] G0.35 CLOSED: 5/5 issued
- [ ] G0.36 CLOSED: 5/5 expired denied
- [ ] G0.37 CLOSED: 5/5 revoked denied
- [ ] Zero kernel modifications
- [ ] Zero V0.5/V0.6 modifications
- [ ] P-Q13 added to PATTERNS.md
- [ ] run_all.py updated (16/16)
- [ ] Commit + tag v0.7.4

## 9. Signature

Status: FROZEN
Version: v0.7.4
Date: 2026-09-22
Reference: FREEZE_v0.7.4 (rev1)

Immutable after freeze:
1. Scope (delegation.py only)
2. Pattern P-Q13 fields and rules
3. Thresholds in section 5
4. Gate definitions in section 6

Editable after freeze:
- Internal delegation.py implementation
- Test infrastructure
- PATTERNS.md prose

Rule: Kernel untouched. V0.5/V0.6 untouched.

---
END OF FREEZE v0.7.4
