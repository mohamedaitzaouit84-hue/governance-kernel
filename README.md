# Governance Kernel

**A minimal-dependency governance kernel for AI agents.**
Built on a single Android phone, with zero budget.
Six gates closed. 54/54 attacks blocked. PRI = 1.0000.

**Latest DOI (V0.6)**: [10.5281/zenodo.22812967](https://doi.org/10.5281/zenodo.22812967)
**V0.5 DOI**: [10.5281/zenodo.22773365](https://doi.org/10.5281/zenodo.22773365)
**Concept DOI** (all versions): [10.5281/zenodo.22773364](https://doi.org/10.5281/zenodo.22773364)

Author: Ahmed Ait Zaouit (Morocco)
Repository: https://github.com/mohamedaitzaouit84-hue/governance-kernel

---

## What this is

A working implementation of governance-first architecture:

- **Governance before governed.** The kernel exists before the agents.
- **Freeze before code.** Every version is frozen (docs/FREEZE_vN.md)
  before a single line of code is written.
- **Pre-registered thresholds.** Attack success rates are declared
  before running tests. No post-hoc adjustment.
- **Failures are logged.** See docs/JOURNEY.md. Nothing is hidden.
- **One external dependency.** cryptography (Ed25519), for the trust anchor only. Everything else is Python standard library.

Read docs/OPENING.md first — it defines what this project does
and does NOT claim.

---

## Status

| Version | Status | Evidence |
|---------|--------|----------|
| V0.1 Kernel | CLOSED | d4d776c |
| V0.2a Memory | CLOSED | 0926b4d |
| V0.3 Separation | 2/3 gates | 0ad9360 |
| V0.4 Attacks | CLOSED (PRI = 1.0000) | e67ec7f |
| **V0.5 Agents** | **CLOSED (5/5 gates)** | 6000b11 |

Full V0.5 report: docs/GATES_v0.5_report.md

---

## What it protects against

V0.4 attack suite (5 attacks, 54 cases):

| Attack | Cases | Kernel |
|--------|-------|--------|
| a1 prompt injection | 10 | 10/10 |
| a2 role spoofing | 12 | 12/12 |
| a3 confused deputy | 12 | 12/12 |
| a4 token theft | 8 | 8/8 |
| a5 subagent compromise | 12 | 12/12 |
| **Aggregate** | **54** | **54/54, PRI = 1.0000** |

Baselines for comparison:

| System | Blocked | PRI |
|--------|---------|-----|
| Baseline-A (no gate) | 0/54 | 0.0000 |
| Baseline-B (whitelist) | 41/54 | 0.7593 |
| **Kernel** | **54/54** | **1.0000** |

Pre-registered threshold: 0.95. Result: 1.0000. Unchanged.

---

## Architecture

    governance_kernel/
    ├── CHARTER.md             Founding charter + 10 binding principles
    ├── LICENSE                AGPL v3 + dual-license notice
    ├── SECURITY.md            Vulnerability disclosure policy
    ├── AUTHORS.md             Author identity and links
    ├── README.md              This file
    ├── docs/                  20+ reference documents
    │   ├── OPENING.md         Integrity protocol
    │   ├── HANDOVER.md        Session transfer protocol
    │   ├── PATTERNS.md        16 architectural patterns
    │   ├── GATES.md           Pre-registered gates
    │   ├── JOURNEY.md         Every error, documented
    │   ├── PRIOR_ART.md       Honest comparison with existing work
    │   ├── FREEZE_v0.*.md     Frozen specs per version
    │   └── GATES_v0.*_report  Gate reports
    ├── seed/                  Trust anchor (Ed25519)
    ├── audit/                 Hash-chained append-only log
    ├── policy/                Signed policy + policy engine
    ├── authorization/         Gate, registry, branches
    ├── control/               Kill switch, resource governor
    ├── memory/                V0.2a episodic + semantic
    ├── kernel/separation/     V0.3 Info/Policy/Node separation
    ├── agents/                V0.5 deterministic agents
    └── tests/
        ├── gate_v03/          G0.7, G0.9
        ├── gate_v04/          5 attacks + 2 baselines
        └── gate_v05/          G0.13 - G0.17

---

## Novel patterns

Documented in docs/PATTERNS.md:

- **P-L1** Dynamic Trust Score
- **P-Q8** Progressive Capability
- **P-Q9** Base Invariants
- **P-Q11** Policy Extension (Layered Permissions)
  - Inspired by canon law, federalism, Kubernetes CRDs
  - Base policy signed and untouched. Extensions merged at runtime.
  - Empirically verified: V0.4 PRI unchanged after V0.5 additions.

---

## Hypotheses tested

| Hyp | Statement | Status |
|-----|-----------|--------|
| H1  | Dynamic Trust | Tested (G0.15) |
| H6  | Single Authority | Tested (V0.2a) |
| H7  | Dual Verification | Tested (V0.2a) |
| H8  | Layered Trust | Tested (V0.3) |
| H9  | Resource Justice | Tested (V0.3) |
| H10 | Trust as Permission | Tested (V0.3) |
| H13 | Progressive Capability | Tested (V0.5) |
| H14 | Base Invariants | Tested (G0.16) |
| H16 | Policy Extension | Tested (V0.5, V0.4 regression) |

Untested hypotheses are listed in docs/PATTERNS.md.

---

## Quick start

    git clone https://github.com/mohamedaitzaouit84-hue/governance-kernel
    cd governance_kernel

    # Verify audit chain
    python audit/integrity.py

    # Run V0.4 attack suite
    python tests/gate_v04/run_all.py

    # Run V0.5 gate suite
    python tests/gate_v05/run_all.py

Requires Python 3.9+ and one external package: cryptography (used only by seed/root.py for Ed25519). Install with: pip install cryptography
Total runtime: under 30 seconds on a phone.

---

## What this project does NOT claim

See docs/OPENING.md and docs/PRIOR_ART.md for the full list.

- Not the first governance kernel (OPA, Cedar exist).
- Not production-ready (no external red team).
- Not formally verified (informal only).
- Not superior to OPA or Cedar (see PRIOR_ART.md section "Weaker").

---

## License

- **Code**: AGPL v3 (or commercial license on request)
- **Documentation**: CC BY-SA 4.0
- **Trademark**: "Governance Kernel" reserved

See LICENSE for details.

---

## Contact

Ahmed Ait Zaouit
mohamedaitzaouit84-hue@users.noreply.github.com
Morocco

Built on a phone, at zero cost.

---

*Last updated: 2026-09-15 — V0.5 CLOSED*
