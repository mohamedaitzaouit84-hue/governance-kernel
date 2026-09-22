# FREEZE — V0.7.9 (Empty Audit Log Self-Healing)

**Version**: v0.7.9
**Status**: FROZEN
**Date**: 2026-09-22
**Parent**: docs/FREEZE_v0.7.7.md
**Trigger**: J-0.8.7 (empty audit.jsonl breaks append)
**Scope**: Fix _read_last() to handle empty log
**Rule**: This document is read before any V0.7.9 code.

---

## 0. Fourth Targeted Fix

V0.7.6: seed/root.py (one line).
V0.7.7: 7 files (Path Portability).
V0.7.8: bootstrap.py + G0.34.
V0.7.9: audit/append_only_log.py (self-healing).

V0.7.9 modifies ONE file:
  audit/append_only_log.py

This file is in V0.1 (protected by Kernel Untouched).
The deviation is documented.

## 1. Scope Lock

V0.7.9 SHALL modify exactly ONE file:

    audit/append_only_log.py    (fix _read_last)

V0.7.9 SHALL NOT modify any other file.

V0.7.9 SHALL only add:

    docs/FREEZE_v0.7.9.md (this file)
    tests/gate_v07/test_g041_empty_audit_self_heal.py

## 2. The Problem

On a fresh clone:
1. `bootstrap.py` creates `logs/audit.jsonl` as an empty file
2. First `audit.append()` call invokes `_read_last()`
3. `_read_last()` returns None on an empty file
4. `append()` fails: `seq = last["seq"] + 1` -> TypeError
5. V0.5 agents cannot run (every action calls audit.append)

## 3. The Fix

Modify `_read_last()` in `audit/append_only_log.py`:

Before:
    def _read_last():
        if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
            return None

After:
    def _read_last():
        # Self-healing: return synthetic genesis for empty log
        GENESIS = {
            "seq": 0,
            "ts": 0,
            "prev_hash": "0" * 64,
            "kind": "genesis_synthetic",
            "data": {},
            "hash": "0" * 64,
        }
        if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
            return GENESIS
        # ... rest unchanged

This makes append() work correctly on empty logs.
The "seq" of the first real record will be 1.

## 4. Pre-registered Thresholds

| Threshold | Target |
|-----------|--------|
| Files modified | 1 (audit/append_only_log.py) |
| Lines modified | small |
| Other files modified | 0 |
| V0.4 regression | PRI = 1.0000 |
| V0.5 regression | 5/5 |
| V0.6 regression | 5/5 |
| V0.7 regression | 18/18 |
| Colab fresh clone | 18/18 |
| New test G0.41 | CLOSED |

## 5. New Test — G0.41

G0.41 — Empty Audit Log Self-Healing

Criterion:
  - Create an empty audit log (in temp)
  - Call audit.append() once
  - Verify it succeeds (no TypeError)
  - Verify the first record has seq == 1

Method:
  - Use a temporary LOG_PATH via monkey-patching
  - Verify the append returns a valid record

## 6. Threats to Validity

- The synthetic genesis has hash = 64 zeros. A future
  chain verification might flag this as suspicious. The
  fix documents it clearly with kind="genesis_synthetic".
- Alternative: bootstrap.py writes a REAL genesis record.
  This is the cleaner fix but requires modifying
  bootstrap.py again (V0.7.5 file).
- The chosen fix (in _read_last) is self-healing: it works
  regardless of how the log was created (empty, missing,
  fresh).

## 7. Success Criteria

V0.7.9 is CLOSED if and only if:

- [ ] audit/append_only_log.py modified (one function)
- [ ] No other file modified
- [ ] G0.41 CLOSED
- [ ] V0.4 regression: PRI = 1.0000
- [ ] V0.5 regression: 5/5
- [ ] V0.6 regression: 5/5
- [ ] V0.7 regression: 18/18
- [ ] Fresh Colab clone: 18/18
- [ ] Commit + tag v0.7.9

## 8. Signature

Status: FROZEN
Version: v0.7.9
Date: 2026-09-22
Reference: FREEZE_v0.7.9 (rev1)

Immutable after freeze:
1. Scope (1 file)
2. The self-healing approach
3. G0.41

Editable after freeze:
- Test prose

Rule: One fix. One file. Self-healing.
Rule: Documented, not hidden.

---
END OF FREEZE v0.7.9
