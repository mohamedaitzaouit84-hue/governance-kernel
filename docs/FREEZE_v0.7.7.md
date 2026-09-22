# FREEZE — V0.7.7 (Path Portability Phase 2)

**Version**: v0.7.7
**Status**: FROZEN
**Date**: 2026-09-22
**Parent**: docs/FREEZE_v0.7.6.md
**Trigger**: J-0.8.5 (7 files use Path.home())
**Scope**: Fix Path.home() in 7 files, one line each
**Rule**: This document is read before any V0.7.7 code.

---

## 0. Second Explicit Deviation from Kernel Untouched

V0.7.6 fixed ONE file (seed/root.py). External testing
(Colab) revealed the SAME pattern in 6 MORE files.

This is the second explicit deviation. It is larger than
the first (7 files instead of 1).

The deviation is explicit and justified:
- The pattern is systematic (spread across V0.1-V0.5)
- It is invisible on Termux (repo is at $HOME/governance_kernel)
- It is fatal on any other machine (Colab, CI, dev machines)
- Reproducibility is a foundational scientific property

Continuing to avoid the fix would mean every fresh clone
fails V0.5 agents and reproducibility is broken forever.

## 1. Scope Lock

V0.7.7 SHALL modify exactly 7 files, one line each:

V0.1 files:
  audit/append_only_log.py           (line 8)
  audit/integrity.py                 (line 7)
  policy/policy_store.py             (line 8)
  authorization/branch_registry.py   (line 10)
  control/kill_switch.py             (line 10)
  control/resource_governor.py       (line 9)

V0.5 file:
  agents/invariant_checker.py        (line 17)

V0.7.7 SHALL NOT modify any other file.

V0.7.7 SHALL only add:

  docs/FREEZE_v0.7.7.md              (this file)
  tests/gate_v07/test_g040_path_portability_audit.py

## 2. The Fix

For the 6 files using KERNEL_DIR:

    Before:
        KERNEL_DIR = Path.home() / "governance_kernel"
    After:
        KERNEL_DIR = Path(__file__).resolve().parent.parent

For agents/invariant_checker.py:

    Before:
        SANDBOX_ROOT = Path.home() / "governance_kernel" / "agents_sandbox"
    After:
        SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "agents_sandbox"

Behavior:
- Termux: NO CHANGE (same paths)
- Colab/external: NOW CORRECT

## 3. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Files modified | 7 |
| Lines modified per file | 1 |
| Other files modified | 0 |
| V0.4 regression | PRI = 1.0000 |
| V0.5 regression | 5/5 |
| V0.6 regression | 5/5 |
| V0.7 regression | 17/17 |
| New test G0.40 | CLOSED |
| Colab fresh clone | 17/17 |

## 4. New Test — G0.40

G0.40 — Path Portability Audit

Criterion:
  - Scan all V0.1-V0.5 .py files for Path.home() / "governance_kernel"
  - The ONLY allowed occurrences are:
    * tests/gate_v07/test_g039 (test code, not production)
    * tests/gate_v07/test_g040 (audit test, not production)
    * Historical docs/ mentions
  - Production code MUST use __file__-based paths

Method:
  - Python's ast module walks all .py files
  - Detects the banned pattern in production code
  - Fails if any production file uses Path.home() / "governance_kernel"

## 5. Threats to Validity

- This is a targeted fix, not a formal refactor of all
  path handling. Other path patterns (e.g. relative
  imports, sys.path.insert) are not audited.
- Only Path.home() / "governance_kernel" is targeted.
  Other Path.home() usages (if any) may exist in non-.py
  files (shell scripts, docs).
- The fix assumes __file__ is stable across environments.
  This is true for standard Python execution.

## 6. Success Criteria

V0.7.7 is CLOSED if and only if:

- [ ] All 7 files modified (one line each)
- [ ] No other file modified
- [ ] G0.40 CLOSED
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5
- [ ] V0.6 regression: 5/5
- [ ] V0.7 regression: 17/17
- [ ] Fresh Colab clone: 17/17 (after auto-bootstrap)
- [ ] Commit + tag v0.7.7

## 7. Signature

Status: FROZEN
Version: v0.7.7
Date: 2026-09-22
Reference: FREEZE_v0.7.7 (rev1)

Immutable after freeze:
1. The 7 files list
2. The one-line-per-file scope
3. The new test G0.40

Editable after freeze:
- Test prose
- Documentation

Rule: One deviation. Seven files. One pattern.
Rule: Documented, not hidden.

---
END OF FREEZE v0.7.7
