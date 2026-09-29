# FREEZE — v0.7.16

**Type**: Deviation (documented)
**Date**: 2026-09-29
**Predecessor**: v0.7.15 (02884b0)
**Finding**: J-0.8.20

## Section 0 — Deviation Declaration

**Protected file modified**: policy/policies/default.yaml

**Change**: add a new role 'memory_system'.

**Nature**:
  The existing 'system' role has permissions:
    audit:read, audit:write, policy:read, memory:read
  It does NOT have memory:write.

  memory/gate.py:82 sets:
    subj = subject or "memory_system"
  And subjects.json maps 'memory_system' -> role 'system'.

  Therefore memory:write is denied for memory_system,
  and Gate D (tests/gate_d_benchmark.py) fails with:
    MemoryGateError: denied: memory:write

**Scope**:
  - ONE file: policy/policies/default.yaml
  - Additive: a new role. No existing role modified.
  - Required: memory_system needs its own role to write
    memory (Gate D).
  - Also updates bootstrap.py (DEFAULT_SUBJECTS) and
    authorization/subjects.json to point memory_system
    to the new role.

**Alternatives considered and rejected**:

  1. Add 'memory:write' to existing 'system' role.
     Rejected: expands a role used for audit + policy.
     Violates least-privilege.

  2. Remove memory:write requirement from Gate D.
     Rejected: memory:write is legitimate.

  3. Change memory/gate.py:82 default subject.
     Rejected: memory_system is the correct default.

**Adopted**: new role 'memory_system' with memory:*.

## Section 1 — ALLOWED_EXCEPTIONS update

Add to tests/gate_v07/test_g0ZZ_kernel_untouched.py:
    "policy/policies/default.yaml",      # v0.7.16 (J-0.8.20)
    "policy/policies/default.yaml.sig",  # v0.7.16 (J-0.8.42)

## Section 2 — Rationale

G0.ZZ protects policy/. But adding a role is required
to make Gate D work.

The addition is:
  - one role
  - memory:* permissions
  - no change to any existing role

Narrow, additive, documented.

## Section 3 — Constraints

- No change to kernel/.
- No change to existing roles.
- No change to control/, audit/, seed/, memory/.
- No change to any agents/* protected file.
- bootstrap.py + subjects.json updates: role pointer.

## Section 4 — Verification

After applying:
  python tests/gate_d_benchmark.py
Expected:
  Gate D reports results (no memory:write denial).

CI (GitHub Actions) expected:
  V0.4: 54/54, V0.5: 5/5, V0.6: 5/5, V0.7: 19/19.
  G0.ZZ: CLOSED with the new exception.

## Section 5 — Reversibility

Revert = remove the new role + revert role pointer.
100% reversible.

## Section 6 — Precedent

4th scope-lock conflict in the J-0.8.x series:
  - v0.7.6: seed/root.py (J-0.8.3)
  - v0.7.7: 7 files (J-0.8.5)
  - v0.7.15: authorization/subjects.json (J-0.8.28)
  - v0.7.16: policy/policies/default.yaml (J-0.8.20)

Pattern: each is a narrow, additive, documented
exception.
