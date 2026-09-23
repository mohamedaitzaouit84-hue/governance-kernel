# FREEZE — V0.7.11 (Second Dependency Correction)

**Version**: v0.7.11
**Status**: FROZEN
**Date**: 2026-09-23
**Parent**: docs/FREEZE_v0.7.10.md
**Trigger**: J-0.8.9 (PyYAML is a second dependency)
**Scope**: Correct dependency count from 1 to 2
**Rule**: This document is read before any V0.7.11 code.

---

## 0. Documentation + CI Fix Only

V0.7.11 does NOT modify any code file.
- No Python file changes.
- No V0.1-V0.5 files touched.

## 1. Scope Lock

V0.7.11 SHALL modify exactly THREE files:

    .github/workflows/test.yml     (add pyyaml to pip install)
    README.md                      (1 dep -> 2 deps)
    docs/OPENING.md                (1 dep -> 2 deps)

V0.7.11 SHALL NOT modify any other file.

V0.7.11 SHALL only add:

    docs/FREEZE_v0.7.11.md (this file)

## 2. The Correction

Before:
  "One external dependency (cryptography)"

After:
  "Two external dependencies:
   - cryptography (Ed25519, seed/root.py)
   - pyyaml (YAML parsing, policy/policy_store.py)"

GitHub Actions CI (V0.7.10) revealed pyyaml during the
first run: V0.5 failed with ModuleNotFoundError for yaml.

## 3. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Files modified | 3 |
| Dependencies documented | 2 |
| CI pass on Python 3.11/3.12/3.13 | yes |
| Code files modified | 0 |
| V0.7 result on CI | 19/19 |

## 4. Threats to Validity

- The audit script used had 8 false positives (local
  modules not recognized as such). The 2 real deps are
  confirmed by an actual CI failure, not by the script.
- Other stdlib-looking modules might be third-party in
  some Python versions.
- Only tested on Termux, Colab, and GitHub Actions
  ubuntu-latest. Not on macOS or Windows.

## 5. Success Criteria

V0.7.11 is CLOSED if and only if:

- [ ] .github/workflows/test.yml installs both deps
- [ ] README.md lists 2 deps
- [ ] docs/OPENING.md lists 2 deps
- [ ] GitHub Actions reruns and passes on all 3 Python versions
- [ ] V0.7 output on CI = 19/19
- [ ] Commit + tag v0.7.11

## 6. Signature

Status: FROZEN
Version: v0.7.11
Date: 2026-09-23
Reference: FREEZE_v0.7.11 (rev1)

Rule: Documentation + CI only. No code changes.
Rule: Correct the count. Do not hide.

---
END OF FREEZE v0.7.11
