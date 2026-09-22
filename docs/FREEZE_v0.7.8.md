# FREEZE — V0.7.8 (Bootstrap Resigning)

**Version**: v0.7.8
**Status**: FROZEN
**Date**: 2026-09-22
**Parent**: docs/FREEZE_v0.7.6.md
**Trigger**: J-0.8.6 (policy signature invalid after bootstrap)
**Scope**: bootstrap.py re-signs default.yaml after key generation
**Rule**: This document is read before any V0.7.8 code.

---

## 0. Third Targeted Fix

V0.7.6 fixed seed/root.py (one line).
V0.7.7 fixed 7 files (one line each).
V0.7.8 adds a step to bootstrap.py.

No new deviation from Kernel Untouched.

This release ONLY touches `bootstrap.py` (V0.7.5 file) and
`test_g034_v05_untouched.py` (V0.7.7 file for ALLOWED_EXCEPTIONS).

## 1. Scope Lock

V0.7.8 SHALL modify exactly TWO files:

    bootstrap.py                              (add resigning step)
    tests/gate_v07/test_g034_v05_untouched.py (add V0.7.7 exception)

V0.7.8 SHALL NOT modify any other file.

V0.7.8 SHALL only add:

    docs/FREEZE_v0.7.8.md (this file)

## 2. The Problem

On a fresh clone:
1. Git brings `default.yaml` + `default.yaml.sig` (signed
   with the ORIGINAL Termux key)
2. `bootstrap.py` generates a NEW owner key
3. `policy_store.load()` calls `root.verify(hash, sig)`
4. Signature was made with the OLD key -> verification fails
5. V0.5 agents cannot run (policy load raises)

## 3. The Fix

Add a new step to bootstrap.py: `step_policy_signature()`

Logic:
  - Read default.yaml, compute its hash
  - Read default.yaml.sig (hex-encoded signature)
  - Verify with the CURRENT (new) owner key
  - If valid: [SKIP]
  - If invalid: re-sign with the new key, overwrite .sig

This is safe: policy CONTENT is unchanged. Only the
signature is regenerated. This is exactly what
`policy_store.reload_and_resign()` already does.

## 4. G0.34 Update

V0.7.7 modified agents/invariant_checker.py (V0.5 file).
This is a documented deviation (FREEZE_v0.7.7 section 0).

G0.34 (V0.5 Untouched) needs an ALLOWED_EXCEPTIONS set:

    ALLOWED_EXCEPTIONS = {
        "agents/invariant_checker.py",  # V0.7.7 Path Portability
    }

This preserves the spirit of G0.34 (detect UNDOCUMENTED
modifications) while acknowledging documented ones.

## 5. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| bootstrap.py steps | +1 (policy signature) |
| G0.34 exceptions | +1 (invariant_checker.py) |
| V0.4 regression | PRI = 1.0000 |
| V0.5 regression | 5/5 |
| V0.6 regression | 5/5 |
| V0.7 regression | 18/18 |
| Colab fresh clone | 18/18 |
| Other files modified | 0 |

## 6. Threats to Validity

- This fix assumes default.yaml CONTENT is trusted. If a
  malicious party modifies default.yaml AND re-signs it,
  the fix would accept the tampered policy. This is a
  broader security question, out of scope here.
- The fix only covers default.yaml. If other signed files
  exist (future), they would need the same treatment.

## 7. Success Criteria

V0.7.8 is CLOSED if and only if:

- [ ] bootstrap.py has new step_policy_signature()
- [ ] G0.34 updated with ALLOWED_EXCEPTIONS
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5
- [ ] V0.6 regression: 5/5
- [ ] V0.7 regression: 18/18
- [ ] Fresh Colab clone: 18/18
- [ ] Commit + tag v0.7.8

## 8. Signature

Status: FROZEN
Version: v0.7.8
Date: 2026-09-22
Reference: FREEZE_v0.7.8 (rev1)

Immutable after freeze:
1. The scope (2 files)
2. The step name (step_policy_signature)
3. The G0.34 exception

Editable after freeze:
- Implementation details in bootstrap.py
- Test prose

Rule: One fix. Two files. Resolve J-0.8.6.
Rule: Documented, not hidden.

---
END OF FREEZE v0.7.8
