# FREEZE — v0.7.13

**Date**: 2026-09-23
**Predecessor**: v0.7.12 (commit 1198b37)
**Type**: Infrastructure fix (CI reproducibility)
**Finding**: J-0.8.11

## Section 0 — Protected surface (deviation declaration)

**Kernel files touched**: NONE.

**Gate logic touched**: NONE.

**Files changed**:
  - .github/workflows/test.yml  (+2 lines)
  - docs/JOURNEY.md             (J-0.8.11 entry)
  - docs/FREEZE_v0.7.13.md      (this file)

Change is confined to CI configuration. It does not alter
kernel/, authorization/, policy/, control/, audit/, seed/,
memory/, nor any protected agents/* file enforced by G0.ZZ.

.github/workflows/test.yml is NOT in the protected list.
It is execution infrastructure, not governance logic.

## Section 1 — Rationale

J-0.8.11: GitHub Actions runs with shallow clone
(actions/checkout@v4 default fetch-depth: 1). Tags are
absent. G0.34 and G0.ZZ invoke `git diff v0.6-closed HEAD`
to verify protected files were untouched. Diff fails when
the tag is missing -> both gates FAILED on CI.

## Section 2 — Proposed change

.github/workflows/test.yml, in the Checkout step:

  - name: Checkout
    uses: actions/checkout@v4
    with:
      fetch-depth: 0
      fetch-tags: true

## Section 3 — Gate impact prediction

| Gate                    | Before | After              |
|-------------------------|--------|--------------------|
| G0.34 V0.5 Untouched    | FAILED | CLOSED (predicted) |
| G0.ZZ Kernel Untouched  | FAILED | CLOSED (predicted) |
| Other 17 gates          | CLOSED | CLOSED (unchanged) |

Predicted CI result: 19/19.

## Section 4 — Verification protocol

1. Termux: full clone, expect 19/19 (no change).
2. CI push: expect G0.34 and G0.ZZ to CLOSE.
3. If either fails for a different reason, log as
   J-0.8.12 BEFORE any further fix.

## Section 5 — Reversibility

Revert = remove the two added lines. No data migration.
No state change. 100% reversible.

## Section 6 — Constraints

- No change to kernel/ or any protected path.
- No change to gate logic.
- No weakening of audit gates.
- Single commit, single finding, single purpose.
