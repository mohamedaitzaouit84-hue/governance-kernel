# FREEZE — v0.7.15

**Type**: Deviation (documented)
**Date**: 2026-09-24
**Predecessor**: v0.7.14 (commit 0404d22)
**Finding**: J-0.8.28

## Section 0 — Deviation Declaration

**Protected file modified**: `authorization/subjects.json`

**Nature of deviation**:
  `bootstrap.py` (as of v0.7.14, from J-0.8.21) must add
  `"memory_system"` to `authorization/subjects.json` at
  fresh-clone setup. This is required so that
  `memory/gate.py:82` default subject resolution
  (`subj = subject or "memory_system"`) succeeds on fresh clones
  and Gate D can run.

**Scope of deviation**:
  - ONE file: `authorization/subjects.json`
  - Additive only: new subject entries added, never removals
    or modifications of existing entries
  - Deterministic: same addition on all fresh clones
  - Required: no alternative implementation preserves both
    the subject_registry contract and bootstrap correctness

**Alternatives considered and rejected**:

  1. Move subjects.json outside authorization/
     - Rejected: breaks subject_registry.py hardcoded path.

  2. Store memory_system in a separate file
     - Rejected: breaks subject_registry.lookup() single-source
       guarantee.

  3. Never add memory_system to subjects.json
     - Rejected: breaks Gate D (J-0.8.20) on all fresh clones.

  4. Relax PROTECTED_PREFIXES entirely
     - Rejected: opens authorization/ to arbitrary modifications.
       The exception must be narrow.

**Adopted**: Add `authorization/subjects.json` to
  `ALLOWED_EXCEPTIONS` in `test_g0ZZ_kernel_untouched.py` and
  document here.

## Section 1 — ALLOWED_EXCEPTIONS update

Add to `tests/gate_v07/test_g0ZZ_kernel_untouched.py`
(in the `ALLOWED_EXCEPTIONS` set):

    # v0.7.15 (J-0.8.28): bootstrap.py adds default subjects
    # (memory_system) to authorization/subjects.json. Additive
    # only. Required for fresh-clone correctness (J-0.8.21).
    "authorization/subjects.json",

## Section 2 — Rationale

G0.ZZ's `PROTECTED_PREFIXES` includes `"authorization/"`. This was
correct for V0.4-V0.6 because `subjects.json` was effectively
static: it contained only pre-V0.5 subjects (owner, system,
agents) added once in V0.4.1.

V0.7.14 introduced the first new subject after v0.6-closed
(memory_system). The G0.ZZ check compares `v0.6-closed..HEAD`,
so it flagged this addition as a violation.

Without this exception, any future addition of a default subject
would trigger a G0.ZZ failure — meaning that maintenance of
`subjects.json` would be impossible. That is contrary to the
purpose of the exception mechanism (ALLOWED_EXCEPTIONS), which
exists precisely to allow documented, narrow deviations.

## Section 3 — Constraints

- No change to `subjects.json` structure (only additional entries)
- No change to `subject_registry.py`
- No change to `permission_gate.py`
- No change to `policy/`
- No change to `kernel/`, `control/`, `audit/`, `seed/`, `memory/`
- No change to any `agents/*` protected file

## Section 4 — Verification

After applying the exception:

  python tests/gate_v07/test_g0ZZ_kernel_untouched.py

Expected:
  Files changed since v0.6-closed: 62
  No protected files modified.
  G0.ZZ: CLOSED (kernel untouched)

CI (GitHub Actions) expected:
  V0.7 gates: 19/19 closed
  --> V0.7.1 + V0.7.2 + V0.7.3 + V0.7.4 CLOSED

## Section 5 — Reversibility

Revert = remove one line from ALLOWED_EXCEPTIONS.
100% reversible. No data migration.

## Section 6 — Precedent

This is the third scope-lock conflict in the J-0.8.x series:
- J-0.8.3 (v0.7.6): seed/root.py exception for Path.home()
- J-0.8.5 (v0.7.7): 7-file exception for Path.home() portability
- J-0.8.28 (v0.7.15): authorization/subjects.json exception

Pattern: each is a narrow, additive, documented exception required
for correctness on non-Termux environments (CI, Colab, fresh
clones). The kernel itself remains unchanged in behavior; only
path handling and default-subject setup are adapted.

