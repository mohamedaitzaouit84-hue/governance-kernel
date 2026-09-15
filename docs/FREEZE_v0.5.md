# FREEZE — V0.5

**Version**: v0.5.0
**Status**: FROZEN
**Date**: 2026-09-15
**Predecessor**: V0.4-CLOSED (Kernel PRI = 1.0000)
**Files**: docs/FREEZE_v0.5.md (this file)
**Rule**: This document is read before any V0.5 code.

---

## 1. Purpose

Build three deterministic agents governed by the existing Kernel.
No new governance primitives. Only application of existing patterns.

## 2. Scope

IN:
- 3 agents (FileAgent, ComputeAgent, QueryAgent)
- Dynamic trust score
- Progressive capability
- Base invariants per agent
- Governed execution (every action via governed_action)

OUT (Scope Lock):
- No LLM
- No multi-agent consensus
- No distributed registry
- No replication
- No modification to V0.1-V0.4 code

## 3. Applied Patterns

- P-L1: Dynamic Trust Score      (hypothesis H1)
- P-Q8: Progressive Capability   (hypothesis H13)
- P-Q9: Base Invariants          (hypothesis H14)

These three are the ONLY new patterns in V0.5.

---

## 4. Trust Dynamics

- alpha = 0.05   (increment on success)
- beta  = 0.10   (decrement on failure)
- min   = 0.00
- max   = 0.85   (cap — no agent is fully trusted)

Trust is updated only on governed_action outcome.
Every update is logged to audit chain.

## 5. Invariants

Each agent has hard invariants (must always hold):

- FileAgent:    read/write only within sandbox path
- ComputeAgent: numeric ops only, no I/O
- QueryAgent:   read-only, no side effects

Violation -> immediate isolation + trust reset to min.

## 6. Agents and Success Criteria

### 6.1 Agent names
AGENT_NAMES = FileAgent, ComputeAgent, QueryAgent

### 6.2 Metrics
- RUNS_PER_SCENARIO = 10
- N_SCENARIOS = 20
- TOTAL_OPS = 200

### 6.3 Success criteria
- all_agents_run = 3/3
- all_ops_governed = 100%
- no_unregistered_agent = True
- audit_chain_intact = True
- kill_switch_respected = True
- invariants_enforced = 100%
- trust_evolution_logged = True

---

## 7. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Agents registered | 3/3 |
| Governed ops | 100% |
| Unregistered agent blocked | yes |
| Kill Switch obeyed | yes |
| Audit chain integrity | 100% |
| Invariants enforced | 100% |
| Trust evolution logged | 100% |
| Regression vs V0.1-V0.4 | 0 failures |

Thresholds are fixed BEFORE running. No post-hoc adjustment.

## 8. Scope Lock

- Agents: exactly 3
- LLM: none
- Consensus: none
- Replication: none
- Modifications to V0.1-V0.4: none

Any deviation -> V0.5 is not V0.5.

## 9. Hypotheses Under Test

### H1 - Dynamic Trust
Trust evolves per governed_action outcome with bounded dynamics.
Test: run 200 ops, verify trust changes within [0.0, 0.85] and is logged.

### H13 - Progressive Capability
Capabilities are granted in stages as trust grows.
Test: verify agent starts limited, gains permission after N successful ops.

### H14 - Base Invariants
Every agent has hard invariants enforced on every action.
Test: attempt 10 invariant violations, verify all blocked + isolated.

---

## 10. Threats to Validity

- Deterministic agents only (no real LLM)
- Test count limited (20 scenarios, 200 ops)
- Same developer writes tests and code (structural bias)
- No external red team
- H1 / H13 are close to tautology if trust rules are trivial

## 11. Proposed Gates (G0.13 - G0.17)

| Gate  | Name                   | Criterion                       |
|-------|------------------------|---------------------------------|
| G0.13 | Agent Registration     | 3/3 registered with owner sig   |
| G0.14 | Governed Execution     | 100% ops via governed_action    |
| G0.15 | Trust Dynamics         | trust in [0,0.85] and logged    |
| G0.16 | Invariant Enforcement  | 100% violations detected+isolated |
| G0.17 | Kill Switch Respect    | all agents halt immediately     |

Pass rule: 5/5 closed -> V0.5 CLOSED.
4/5 -> V0.5.1 partial.
3 or less -> V0.5 FAILED (document in JOURNEY.md).

## 12. Signature and Freeze

Status: FROZEN
Version: v0.5.0
Date: 2026-09-15
Reference: FREEZE_v0.5 (rev1)

Immutable after freeze:
1. Number of agents (3)
2. Thresholds in section 7
3. Success criteria in section 6.3
4. Scope Lock in section 8

Editable after freeze:
- Internal agent code (no interface change)
- Test infrastructure
- Function names inside agents/

Rule: Failures are logged in JOURNEY.md. Never hidden.

---
END OF FREEZE v0.5
