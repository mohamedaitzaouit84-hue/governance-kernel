# FREEZE — V0.7.3 (Real Agents)

**Version**: v0.7.3
**Status**: FROZEN
**Date**: 2026-09-21
**Parent**: docs/FREEZE_v0.7.md
**Scope**: Integrate real V0.5 agents into V0.6 coordinator
**Rule**: This document is read before any V0.7.3 code.

---

## 1. Purpose

Replace FakeAgent with real V0.5 agents (FileAgent, ComputeAgent,
QueryAgent) in a new coordinator_v2.py.

Test that V0.5 agents can be governed by the V0.6 protocol
without modification to their code.

The V0.6 coordinator.py is NOT modified. A new coordinator_v2.py
is added that uses real agents.

## 2. Scope Lock

V0.7.3 SHALL NOT modify:

    agents/file_agent.py               (V0.5)
    agents/compute_agent.py            (V0.5)
    agents/query_agent.py              (V0.5)
    agents/base_agent.py               (V0.5)
    agents/invariant_checker.py        (V0.5)
    agents/trust_manager.py            (V0.5)
    agents/governed_action_v05.py      (V0.5)
    agents/register_agents.py          (V0.5)
    agents/multi/__init__.py           (V0.6)
    agents/multi/proposal.py           (V0.6)
    agents/multi/consensus.py          (V0.6.1)
    agents/multi/communication.py      (V0.6)
    agents/multi/coordinator.py        (V0.6)
    authorization/*                    (kernel)
    policy/*                           (kernel)
    control/*                          (kernel)
    audit/*                            (kernel)
    seed/*                             (kernel)

V0.7.3 SHALL only add:

    agents/multi/coordinator_v2.py
    tests/gate_v07/test_g031_real_file.py
    tests/gate_v07/test_g032_real_compute.py
    tests/gate_v07/test_g033_real_query.py
    tests/gate_v07/test_g034_v05_untouched.py

## 3. Hypotheses Under Test

### H23 — Real Agents Governed by V0.6 Protocol

Statement: V0.5 agents can be coordinated by the V0.6 protocol
without modification to their code.

Test: 10 real tasks per agent type (file, compute, query).

Pass: 30/30 tasks succeed, 0 V0.5 file changes.

## 4. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Real FileAgent tasks | 10/10 |
| Real ComputeAgent tasks | 10/10 |
| Real QueryAgent tasks | 10/10 |
| V0.5 files modified | 0 |
| Kernel files modified | 0 |
| V0.4 regression | PRI = 1.0000 |
| V0.5 regression | 5/5 |
| V0.6 regression | 5/5 |

Thresholds fixed BEFORE running. No post-hoc adjustment.

## 5. Proposed Gates (G0.31 - G0.34)

| Gate  | Name                          | Criterion |
|-------|-------------------------------|-----------|
| G0.31 | Real FileAgent in Coordinator | 10/10 tasks |
| G0.32 | Real ComputeAgent in Coordinator | 10/10 tasks |
| G0.33 | Real QueryAgent in Coordinator | 10/10 tasks |
| G0.34 | V0.5 agents untouched | git diff = 0 |

Pass rule: 4/4 -> V0.7.3 CLOSED.
3/4 -> V0.7.3 PARTIAL.
2 or less -> V0.7.3 FAILED (JOURNEY.md entry).

## 6. Threats to Validity

- Integration test, not production deployment.
- Only 3 agents tested (not 10+).
- V0.5 agents use governed_action_v05, which requires
  registered subjects (already done in V0.5).
- Test relies on subject_registry from V0.5.
- Devices: single Android device.

## 7. Success Criteria

V0.7.3 is CLOSED if and only if:

- [ ] G0.31 CLOSED: 10/10 file tasks
- [ ] G0.32 CLOSED: 10/10 compute tasks
- [ ] G0.33 CLOSED: 10/10 query tasks
- [ ] G0.34 CLOSED: zero V0.5 modifications
- [ ] Zero kernel modifications
- [ ] V0.4/V0.5/V0.6 regressions pass
- [ ] Commit + tag v0.7.3

## 8. Signature

Status: FROZEN
Version: v0.7.3
Date: 2026-09-21
Reference: FREEZE_v0.7.3 (rev1)

Immutable after freeze:
1. Scope (coordinator_v2.py only)
2. Thresholds in section 4
3. Gate definitions in section 5
4. V0.5 files must remain untouched

Editable after freeze:
- Internal coordinator_v2.py implementation
- Test infrastructure
- Additional tests if needed

Rule: V0.5 untouched. Kernel untouched.

---
END OF FREEZE v0.7.3
