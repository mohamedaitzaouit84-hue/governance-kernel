# FREEZE — V0.7.12 (Bootstrap Branch Registration)

**Version**: v0.7.12
**Status**: FROZEN
**Date**: 2026-09-23
**Parent**: docs/FREEZE_v0.7.11.md
**Trigger**: J-0.8.10 (branches/registry.jsonl not bootstrapped)
**Scope**: Add step_register_branches to bootstrap.py
**Rule**: This document is read before any V0.7.12 code.

---

## 0. Scope: One File

V0.7.12 modifies exactly ONE file:
  bootstrap.py

No V0.1-V0.5 files touched.
No V0.6/V0.7 code files touched.

## 1. The Problem

On a fresh clone:
- `branches/registry.jsonl` is in .gitignore
- `bootstrap.py` (V0.7.5+) initializes identity, logs,
  subjects, policy signature
- But NOT branches
- Result: V0.5 G0.13 fails (0/3 registered)

Detected by GitHub Actions second run (J-0.8.10).

## 2. The Fix

Add `step_register_branches()` to bootstrap.py.

Logic:
  - Import `agents.register_agents`
  - Call its `main()` registration logic
  - Capture output to avoid double-printing

Alternative: run subprocess `python agents/register_agents.py`.
Cleaner: direct import (no subprocess overhead).

Order in main():
  step_owner_key()
  step_root_state()
  step_audit_log()
  step_subjects()
  step_register_branches()   <- NEW
  step_policy_signature()

## 3. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Files modified | 1 (bootstrap.py) |
| Lines added | ~30 |
| Code files modified | 0 |
| CI pass on 3.11/3.12/3.13 | yes |
| V0.5 gates on CI | 5/5 |
| V0.7 gates on CI | 19/19 |

## 4. Threats to Validity

- `register_agents.py` uses `root.sign()` which requires
  the owner key. The order matters: step_owner_key()
  must run first.
- Registration is idempotent (skips existing branches).
  Safe to re-run.
- If branches/registry.jsonl partially exists (corrupt),
  register_agents may fail. Not handled here.

## 5. Success Criteria

V0.7.12 is CLOSED if and only if:

- [ ] bootstrap.py has step_register_branches()
- [ ] Called in main() after step_subjects()
- [ ] CI reruns and passes on all 3 Python versions
- [ ] V0.5 output on CI = 5/5
- [ ] V0.7 output on CI = 19/19
- [ ] Commit + tag v0.7.12

## 6. Signature

Status: FROZEN
Version: v0.7.12
Date: 2026-09-23
Reference: FREEZE_v0.7.12 (rev1)

Rule: One file. One step. Reuse existing code.
Rule: Bootstrap = single source of fresh clone setup.

---
END OF FREEZE v0.7.12
