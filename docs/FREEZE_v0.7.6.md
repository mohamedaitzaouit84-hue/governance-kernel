# FREEZE — V0.7.6 (Path Portability)

**Version**: v0.7.6
**Status**: FROZEN
**Date**: 2026-09-22
**Parent**: docs/FREEZE_v0.7.md
**Trigger**: J-0.8.3 (Path.home in seed/root.py)
**Scope**: Fix one line in seed/root.py for path portability
**Rule**: This document is read before any V0.7.6 code.

---

## 0. Explicit Deviation from Kernel Untouched

V0.7.6 BREAKS the "Kernel Untouched" rule for ONE LINE.

The deviation is explicit and justified:

- V0.1 (seed/root.py) uses `Path.home() / "governance_kernel"`
- This assumes the repo is always at `$HOME/governance_kernel`
- On Termux: true. On Colab: false. On any other machine: not guaranteed.
- Result: `bootstrap.py` writes keys to `/root/governance_kernel/` on Colab
  while the repo is at `/content/governance-kernel/`
- Consequence: V0.5 agents fail; reproducibility is broken.

Fix: change ONE LINE in `seed/root.py`:

    Before:  KERNEL_DIR = Path.home() / "governance_kernel"
    After:   KERNEL_DIR = Path(__file__).resolve().parent.parent

This is the ONLY change in this release.

## 1. Scope Lock

V0.7.6 SHALL modify exactly ONE file:

    seed/root.py        (one line, the KERNEL_DIR definition)

V0.7.6 SHALL NOT modify any other file.

V0.7.6 SHALL only add:

    docs/FREEZE_v0.7.6.md (this file)
    tests/gate_v07/test_g039_path_portability.py

## 2. Rationale

The "Kernel Untouched" rule (from FREEZE_v0.7 section 0) exists
to preserve stability and compatibility. It is not absolute.

When an external test reveals a foundational defect, the
defect must be fixed — otherwise reproducibility remains
broken forever.

Continuing to avoid the fix would mean:
- Every fresh clone fails on V0.5 agents
- Every external reviewer finds the same defect
- The project cannot honestly claim reproducibility

Fixing the defect openly, with documentation, is the
scientific choice.

## 3. What Changes

File: seed/root.py
Line: 8 (originally)

Before:
    KERNEL_DIR = Path.home() / "governance_kernel"

After:
    KERNEL_DIR = Path(__file__).resolve().parent.parent

Behavior:
- Termux: NO CHANGE (KERNEL_DIR resolves to same path)
- Colab: NOW CORRECT (KERNEL_DIR = /content/governance-kernel)
- Any machine: NOW CORRECT

## 4. What Does NOT Change

- All other lines in seed/root.py
- All other files in seed/
- All V0.1-V0.7 behavior on Termux
- All tests in tests/gate_v03/ ... tests/gate_v07/

## 5. New Test

G0.39 — Path Portability

Criterion:
  - `seed.root.KERNEL_DIR` resolves to the repository root
  - Independent of `Path.home()`
  - Verified by comparing to `Path(__file__).parent.parent`
  - No regression: all V0.4/V0.5/V0.6/V0.7 tests still pass

Test file:
  tests/gate_v07/test_g039_path_portability.py

## 6. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Files modified | 1 (seed/root.py) |
| Lines modified | 1 |
| Other files modified | 0 |
| Regression V0.4 | PRI = 1.0000 |
| Regression V0.5 | 5/5 |
| Regression V0.6 | 5/5 |
| Regression V0.7.1-V0.7.4 | 16/16 |
| G0.39 | CLOSED |

## 7. Threats to Validity

- This is a targeted fix, not a systematic review of
  Path.home() usage elsewhere in the codebase.
- Other V0.1 files MAY also use Path.home(); a future
  audit is required.
- The fix has only been tested on Termux and Colab,
  not on a wide range of environments.

## 8. Success Criteria

V0.7.6 is CLOSED if and only if:

- [ ] seed/root.py KERNEL_DIR changed (one line)
- [ ] No other file modified (except FREEZE and test)
- [ ] G0.39 CLOSED
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5
- [ ] V0.6 regression: 5/5
- [ ] V0.7 regression: 16/16
- [ ] Fresh Colab clone: 16/16 after bootstrap
- [ ] Commit + tag v0.7.6

## 9. Signature

Status: FROZEN
Version: v0.7.6
Date: 2026-09-22
Reference: FREEZE_v0.7.6 (rev1)

Immutable after freeze:
1. The one-line change
2. The scope (one file only)
3. The justification (documented deviation)

Editable after freeze:
- The new test file
- This document's prose

Rule: One deviation. One line. One fix.
Rule: Documented, not hidden.

---
END OF FREEZE v0.7.6
