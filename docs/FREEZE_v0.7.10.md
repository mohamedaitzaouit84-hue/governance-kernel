# FREEZE — V0.7.10 (GitHub Actions CI)

**Version**: v0.7.10
**Status**: FROZEN
**Date**: 2026-09-23
**Parent**: docs/FREEZE_v0.7.9.md
**Trigger**: J-0.8.8 (dependency audit needed automated check)
**Scope**: Add GitHub Actions workflow for continuous testing
**Rule**: This document is read before any V0.7.10 code.

---

## 0. No Deviation from Kernel Untouched

V0.7.10 does NOT touch any V0.1-V0.5 file.
V0.7.10 does NOT modify any code.
V0.7.10 adds CI infrastructure only.

## 1. Purpose

Add a GitHub Actions workflow that runs the full test
suite (V0.4, V0.5, V0.6, V0.7) on every push. This
automates the reproducibility check.

Triggered by:
- J-0.8.8: discovering cryptography is a hidden dependency
- 8 total reproducibility defects found by external testing
- Need to prevent future regressions automatically

## 2. Scope Lock

V0.7.10 SHALL add exactly ONE file:

    .github/workflows/test.yml

V0.7.10 SHALL modify exactly ONE file:

    README.md (add CI status badge)

V0.7.10 SHALL NOT modify any code file.

V0.7.10 SHALL only add:

    docs/FREEZE_v0.7.10.md (this file)

## 3. The Workflow

File: .github/workflows/test.yml

Trigger:
- push to main
- pull_request to main
- manual (workflow_dispatch)

Matrix:
- Python 3.11
- Python 3.12
- Python 3.13

Steps per job:
1. Checkout code
2. Set up Python (matrix version)
3. pip install cryptography (the single dependency)
4. python bootstrap.py
5. python tests/gate_v04/run_all.py
6. python tests/gate_v05/run_all.py
7. python tests/gate_v06/run_all.py
8. python tests/gate_v07/run_all.py

Pass criterion: all four test suites exit 0.

## 4. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| CI file added | .github/workflows/test.yml |
| Python versions | 3 |
| Test suites run | 4 (V0.4-V0.7) |
| Expected result on ubuntu-latest | 19/19 for V0.7 |
| Code files modified | 0 |
| Dependencies installed | 1 (cryptography) |

## 5. Threats to Validity

- GitHub Actions uses a specific ubuntu-latest image that
  may not match production or Termux behavior.
- The runner has 4 CPU cores and 16 GB RAM. Performance
  tests (G0.28, G0.30) will be much faster than on a phone.
- Time-sensitive tests (G0.36, J-0.8.7) may behave
  differently under CI's process isolation.
- cryptography version on CI may differ from Termux's.
- The CI may pass while a real edge case on another
  platform fails (or vice versa).

## 6. Success Criteria

V0.7.10 is CLOSED if and only if:

- [ ] .github/workflows/test.yml exists
- [ ] README.md has CI badge
- [ ] CI runs on GitHub (visible in Actions tab)
- [ ] CI passes on all 3 Python versions (3.11, 3.12, 3.13)
- [ ] CI output shows 19/19 for V0.7
- [ ] No code files modified
- [ ] Commit + tag v0.7.10

## 7. Signature

Status: FROZEN
Version: v0.7.10
Date: 2026-09-23
Reference: FREEZE_v0.7.10 (rev1)

Immutable after freeze:
1. The workflow file scope
2. Python versions matrix
3. Test suites order

Editable after freeze:
- Workflow step names
- Badge style
- Comments

Rule: CI-only. No code changes.
Rule: External environment as final check.

---
END OF FREEZE v0.7.10
