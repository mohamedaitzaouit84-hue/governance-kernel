# HANDOVER — Session Transfer Document

**Date**: 2026-09-15
**Purpose**: Transfer project state to a new session without losing context.
**Rule**: This document is read FIRST in any new session.

---

## 1. Project Identity

- Name: Governance Kernel
- Repo: github.com/mohamedaitzaouit84-hue/governance-kernel (Private)
- Purpose: Governance kernel controlling AI agents
- Device: single phone (Termux)
- Cost: 0 MAD
- Methodology: Governance-First Architecture

## 2. Reading Order (new session)

1. CHARTER.md
2. docs/HANDOVER.md (this file)
3. docs/PATTERNS.md
4. docs/GATES.md
5. docs/FREEZE_v0.5.md
6. docs/DECISIONS.md
7. docs/JOURNEY.md

## 3. Current State

### Completed
| Version | Status | Last commit |
|---------|--------|-------------|
| V0.1 (Kernel) | CLOSED | d4d776c |
| V0.2a (Memory) | CLOSED | 0926b4d |
| V0.3 (Separation) | 2/3 gates | 0ad9360 |
| V0.4 (Attacks) | CLOSED | e67ec7f |
| V0.4.1 (Registry) | fix | 1f26943 |
| PATTERNS.md | written | 030ce06 |
| **V0.5 (Agents)** | **✅ CLOSED** | **8cd93d4** |

### In Progress
None. V0.5 closed. Next: V0.6 or publish V0.4.

### Not Started
- V0.6 local LLM
- V0.7 multi-agent + consensus
- V0.8+ distributed registry, self-evolution

---

## 4. Critical Numbers

### V0.4 attack results
| System | Blocked | PRI |
|--------|---------|-----|
| Baseline-A (no gate) | 0/54 | 0.0000 |
| Baseline-B (whitelist) | 41/54 | 0.7593 |
| Kernel | 54/54 | 1.0000 |

Pre-registered threshold: 0.95 -> passed.

### V0.3 separation results
- G0.7 Policy Separation: kappa=0.034 (threshold 0.2) -> CLOSED
- G0.9 Repeatability: 240/240 (100%) -> CLOSED
- G0.11 Counterfactual: FAILED (finding documented)

### General inventory
- Commits: ~30
- Lines of code: ~2500
- Lines of docs: ~4000
- Reference docs: 17+
- Patterns: 15
- Testable hypotheses: 15 (H1-H15)
- Attack tests: 5 (54 cases)

## 5. Architecture

Repo layout:
- CHARTER.md, README.md
- docs/ (17+ documents)
- seed/ (Trust Anchor, Ed25519)
- audit/ (Hash-chained log)
- policy/ (Signed policy)
- authorization/ (Gate, Registry, Branches)
- control/ (Kill Switch, Resources)
- memory/ (V0.2a)
- kernel/separation/ (V0.3)
- tests/ (gate_v03/, gate_v04/, gate_v05/)

Protected by .gitignore (never upload):
- identity/owner_key.priv
- identity/root_state.json
- logs/*.jsonl
- control/kill.flag, control/resource_state.json
- branches/registry.jsonl
- __pycache__/, *.pyc

---

## 6. Next Session Plan

### Phase 1 — Upload V0.5 FREEZE + HANDOVER (5 min)
git add -A
git commit -m "freeze(v0.5) + handover"
git push
git log --oneline -3

### Phase 2 — Build agents (2-3 hours)
Order, in small blocks:

1. agents/__init__.py + agents/base_agent.py (~100 lines)
2. agents/trust_manager.py (P-L1 + P-Q8, ~80 lines)
3. agents/invariant_checker.py (P-Q9, ~60 lines)
4. agents/file_agent.py + compute_agent.py + query_agent.py (~200 lines)
5. agents/register_agents.py (~50 lines)
6. tests/gate_v05/test_agents_basic.py (~80 lines)
7. tests/gate_v05/test_dynamic_trust.py (H1, ~80 lines)
8. tests/gate_v05/test_progressive.py (H13, ~80 lines)
9. tests/gate_v05/test_invariants.py (H14, ~80 lines)
10. tests/gate_v05/test_kill_switch_agents.py (~60 lines)
11. docs/GATES_v0.5_report.md (PRI, findings, threats)

### Phase 3 — if V0.5 succeeds
Option A: publish V0.4 on GitHub public.
Option B: start V0.6 (local LLM).

## 7. Governing Rules

1. Governance before governed.
2. Freeze before code. Every version frozen first.
3. Failures are logged. Never hidden.
4. Thresholds pre-registered. Never adjusted post-hoc.
5. No LLM before V0.6 (Scope Lock).

## 8. Code Rules

1. No religious/philosophical terms in code. Engineering only.
2. No import from AZ Research. Separate projects.
3. No more than 3 agents in V0.5 (Scope Lock).
4. Every operation goes through governed_action. No exception.

## 9. Termux Rules

1. Small blocks beat big blocks.
2. Ctrl+C exits stuck heredoc.
3. wc -l verifies write success.
4. git log --oneline -3 after each push.
5. Avoid backticks in heredoc.
6. No /tmp in Termux. Use $HOME.

---

## 10. Hypotheses (PATTERNS.md)

### Tested
- H6 Single Authority
- H7 Dual Verification
- H8 Layered Trust
- H9 Resource Justice
- H10 Trust as Permission

### Under test in V0.5
| Hypothesis | Test file |
|------------|-----------|
| H1 Dynamic Trust | test_dynamic_trust.py |
| H13 Progressive Capability | test_progressive.py |
| H14 Base Invariants | test_invariants.py |

### Deferred
- H2, H3, H4, H5, H11, H12, H15

## 11. Open Risks

### Methodological
- Tests written by same developer (structural bias)
- No external red team yet
- Real LLM not tested

### Technical
- Audit log grows without rotation
- Not tested on multiple devices
- Not tested at 1000-op scale

### Strategic
- No market, no client, no team
- Zero budget (intentional)
- No formal certifications

## 12. Long-Term Horizon

- V0.6 local LLM
- V0.7 multi-agent + consensus
- V0.8+ distributed registry
- V0.9+ self-evolution governed
- arXiv paper (6-12 months)
- Public GitHub release
- Small bug bounty
- Partnership with Moroccan entity

## 13. Session Start Protocol

First message in new session:
"I am working on Governance Kernel.
Read docs/HANDOVER.md first.
Last commit: [paste last commit].
Continue V0.5."

Also run at session start:
python audit/integrity.py | head -3
git log --oneline -3
git status --short

If integrity is not ok: STOP. Read docs/JOURNEY.md.

## 14. Session Notes

- Previous session: 8+ hours
- Mental state: excellent
- Performance: 30 commits in 2 days
- Stop was natural, not failure

This document is read in every new session before any work.
END OF HANDOVER
