# OPENING — Integrity Protocol

**Rule**: This document is read BEFORE opening any new version.
**Purpose**: Enforce scientific integrity. No decoration. No emotion.

---

## 1. What this project IS NOT

We refuse the following claims:

- "First governance kernel for AI" — FALSE. Others exist (OPA, Cedar).
- "Novel architecture" — PARTIALLY. Components exist. Assembly is new.
- "Production-ready" — FALSE. No red team. Deterministic agents only.
- "Secure" — FALSE. No external audit. No formal verification.
- "Revolutionary" — FALSE. It is a careful application of known patterns.

Any document claiming otherwise must be corrected or removed.

## 2. What this project IS

- A working proof that governance-first design is possible
  at zero cost, on a single device, with zero dependencies.
- A methodical application of freeze-before-code discipline.
- A reproducible reference for others to compare against.
- An honest record of failures (see JOURNEY.md).

## 3. Required before every new version

Before starting Vx.y:

- [ ] Write FREEZE_vX.md first
- [ ] Pre-register thresholds (no post-hoc adjustment)
- [ ] List hypotheses to test (falsifiable)
- [ ] State scope lock (IN vs OUT)
- [ ] Compare with at least 2 existing alternatives
- [ ] Declare expected failure modes

After closing:

- [ ] Report actual numbers vs pre-registered
- [ ] Log every deviation from expectations
- [ ] Document threats to validity
- [ ] If a gate fails: document in JOURNEY.md, do not hide

## 4. Language rules

- Banned in technical docs: "powerful", "revolutionary",
  "cutting-edge", "state-of-the-art", "game-changing".
- Claims require test files. No test -> no claim.
- Numbers must be reproducible. Cite the file that produces them.
- Comparisons must include cases where the project LOSES.

## 5. Priority and authorship

- Every release archived on Zenodo with a DOI.
- Author identity anchored to an existing ORCID profile.
- Any derivative must retain attribution (AGPL v3 / CC BY-SA 4.0).
- The author's academic record is public and citable.

## 6. Admission of limits

This project has:

- One developer (structural bias).
- No external red team (unvalidated claims).
- No formal verification (informal only).
- No production deployment (theoretical + test-verified).
- No LLM in the loop (deterministic only, as of V0.5).
- Zero budget (which also means zero influence).
- **One external dependency** (see below).

We declare these limits UP FRONT, in every version report.

### Known dependencies

The project has exactly ONE external dependency:

- **cryptography** — used only in `seed/root.py` for
  Ed25519 key generation, signing, and verification.

All other code uses the Python standard library only.

The original `CHARTER.md` stated "zero external
dependencies." That was the aspiration. Reality is
"one dependency, deliberately minimal, and fully
accounted for."

This correction was made on 2026-09-23 after an audit
triggered by preparing a GitHub Actions workflow. See
`docs/JOURNEY.md` J-0.8.8 for the full context.

Any future claim of "zero-dependency" in this project
must be replaced by "minimal-dependency" or by an
explicitly qualified statement.

## 7. Comparison with existing work — mandatory

Every new version must state:

- What already exists (see docs/PRIOR_ART.md).
- What this project does differently (if anything).
- Where this project is WEAKER than existing solutions.

If this section is empty, the version is not complete.

## 8. Authorship and continuity

This project is part of a longer line of work by the author.
Previous publications (ORCID, Zenodo) are the foundation.
Future publications must cite both past and present work.

Integrity means: same name, same identity, same standards,
across every release.

---

**Signed**: The author commits to reading this document before every
version opening. Commitments to integrity outweigh commitments to
appearance.

**Version**: 1.0 — 2026-09-15
