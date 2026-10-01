# FREEZE — v0.7.19

**Type**: Bugfix plan (from external red team)
**Date**: 2026-10-01
**Predecessor**: v0.7.18 (015e0bc)
**Findings addressed**: J-0.8.50, J-0.8.51, J-0.8.52,
                         J-0.8.53, J-0.8.54, J-0.8.55,
                         J-0.8.56, J-0.8.57, J-0.8.58
**Source**: docs/RED_TEAM_v0.7.18_AI_ASSISTED.md
**Status**: PLANNED (not yet frozen)

## Section 0 — Deviation Declaration

**Protected files to be modified**: TBD.

The fixes for J-0.8.50-53 target files that are inside
PROTECTED_PREFIXES (audit/, control/, seed/). Therefore
this FREEZE will require an update to ALLOWED_EXCEPTIONS
in tests/gate_v07/test_g0ZZ_kernel_untouched.py.

The specific list will be finalized when each sub-fix
is implemented. For now this section declares the
intent.

The fixes for J-0.8.54-56 target bootstrap.py and
authorization/, which are also protected in part
(authorization/subjects.json is in ALLOWED_EXCEPTIONS
already).

## Section 1 — Scope

### J-0.8.53 — Encrypt the owner key (CRITICAL)

**File**: seed/root.py
**Change**: generate_owner_key() and load_owner_key()
accept an optional passphrase. If provided, the PEM is
encrypted with PKCS#8 (AES-256 + PBKDF2-HMAC-SHA256,
600,000 iterations, or Argon2id if available).
**Compatibility**: if no passphrase is provided, keep
the current behaviour (unencrypted) and print a
warning. The default in bootstrap.py becomes: prompt
for a passphrase if TTY is attached, else keep
unencrypted.
**Tests**: existing V0.5/V0.7 should pass unchanged.
A new test verifies that a passphrase-protected key
cannot be loaded without the passphrase.

### J-0.8.50 — Sign every audit record (CRITICAL)

**File**: audit/append_only_log.py
**Change**: each record gains an Ed25519 signature
over `f"{seq}|{ts}|{prev_hash}|{kind}|{hash}"`.
verify_chain() requires a valid signature per record.
**Cost**: one Ed25519 signature per append
(~5-10 ms on Termux).
**Tests**: V0.7 G0.41 (audit self-heal) must pass.
A new test verifies that a forged record without a
matching signature is rejected.

### J-0.8.52 — Kill switch as signed audit state (CRITICAL)

**File**: control/kill_switch.py
**Change**: is_active() reads the audit log for the
latest kill_switch_triggered / kill_switch_cleared
record, rather than FLAG.exists(). The FLAG file
becomes a cache.
**Tests**: G0.17 must pass. A new test verifies that
deleting control/kill.flag does not disable the
switch if the audit contains a trigger.

### J-0.8.51 — External anchor (CRITICAL, depends on J-0.8.50)

**File**: (new) audit/anchor.py + release process
**Change**: after each release, publish the current
head_hash and length in the GitHub Release notes and
in the Zenodo metadata. Provide a script
`python audit/verify_anchor.py` that checks the local
log against the published values.
**Tests**: no automatic test (the anchor is external).
Document the manual procedure in HANDOVER.md.

### J-0.8.55 — Sign subjects.json (PARTIAL)

**File**: authorization/subject_registry.py,
              authorization/subjects.json
**Change**: add owner_signature_hex to subjects.json,
computed over the canonical JSON serialization.
subject_registry.load() verifies on read.
**Tests**: V0.5 G0.13 must pass. A new test verifies
that a tampered subjects.json is rejected.

### J-0.8.54 — Bootstrap requires consent to re-sign (PARTIAL)

**File**: bootstrap.py
**Change**: step_policy_signature() prints the policy
hash and, if the signature does not verify, requires
`--accept-policy <hash>` on the command line. Without
the flag, bootstrap exits with a non-zero code and an
explanatory message.
**Tests**: bootstrap must still work in CI (add the
flag to the CI invocation). A new test verifies that
bootstrap refuses to re-sign without the flag.

### J-0.8.56 — Audit length anchor (PARTIAL)

**File**: audit/integrity.py
**Change**: maintain a small file logs/audit.lock
with the highest seq seen and its hash, updated
atomically. verify_chain() refuses a log whose last
seq is lower than the recorded highest.
**Tests**: V0.7 G0.41 must pass. A new test verifies
that tail truncation is detected.

### J-0.8.57 — Authorize resource_governor.reset() (CRITICAL)

**File**: control/resource_governor.py
**Change**: reset() requires a signed authorization:

    def reset(signature_hex, message):
        if not root.verify(message.encode(), bytes.fromhex(signature_hex)):
            return False
        STATE.unlink(missing_ok=True)
        audit.append("resource_state_reset", {"message": message})
        return True

  Without a valid signature, reset() returns False and
  leaves the state untouched.
**Tests**: G0.28-30 must pass. A new test verifies that
reset() without a signature does not delete the state.

### J-0.8.58 — Sign rotation_manifest (CRITICAL)

**File**: audit/rotation.py
**Change**: each manifest entry gains:
  - an Ed25519 signature over
    f"{ts}|{archived}|{prev_last_seq}|{prev_last_hash}|{new_genesis_hash}"
  - a `prev_manifest_hash` field linking to the previous
    entry (manifest chain)
**Tests**: rotation tests must pass. A new test verifies
that a tampered manifest is detected.
**Depends on**: J-0.8.50 (sign every audit record), so
that the root sign() is already available in the
rotation path.

## Section 2 — Pre-registered Thresholds

No new thresholds. All existing gates must continue
to pass (V0.5 = 5/5, V0.7 = 19/19).

## Section 3 — Order of Implementation

The order reflects dependency:

  1. J-0.8.53 (key encryption) — root of trust.
  2. J-0.8.50 (signed records) — protects the audit.
  3. J-0.8.52 (signed kill state) — depends on
     J-0.8.50 for reading the audit.
  4. J-0.8.51 (external anchor) — depends on J-0.8.50.
  5. J-0.8.55 (signed subjects) — independent.
  6. J-0.8.54 (bootstrap consent) — independent.
  7. J-0.8.56 (length anchor) — depends on J-0.8.50.
  8. J-0.8.57 (governor reset authorization) —
     independent (uses root.verify directly).
  9. J-0.8.58 (signed manifest) — depends on J-0.8.50.

## Section 4 — Non-goals

The following are NOT part of v0.7.19:

  - Changing the kernel loop (kernel/).
  - Changing the V0.4-V0.7 gate criteria.
  - Adding new external dependencies.
  - Changing the threat model position of v0.7.18
    (same-user attacker remains out of scope by
    default; the fixes are defence-in-depth for users
    who opt in).

## Section 5 — Verification Plan

After all sub-fixes are implemented:

  - CI: green on Python 3.11, 3.12, 3.13.
  - Termux: V0.5 = 5/5, V0.7 = 19/19.
  - Colab: same, fresh clone.
  - Re-run the three rounds of the AI-assisted red
    team. Expected: J-0.8.50-56 no longer reproduce.
  - Publish v0.7.19 with the head_hash in the release
    notes (the first external anchor).

## Section 6 — Timeline

  - J-0.8.53: 1 day
  - J-0.8.50: 1 day
  - J-0.8.52: 1 day
  - J-0.8.51: 4 hours
  - J-0.8.55: 1 day
  - J-0.8.54: 2 hours
  - J-0.8.56: 4 hours
  - J-0.8.57: 3 hours
  - J-0.8.58: 2 hours (after J-0.8.50)

  Total: ~6 working days.

## Section 7 — Status

**PLANNED.** This FREEZE becomes active when the
first sub-fix (J-0.8.53) is started. Until then, it
is a plan, not a commitment.

The plan may be revised if the implementation reveals
that a sub-fix is more complex than estimated, or
that a different fix is preferable.

## Section 8 — Scientific Note

This is the first FREEZE written in response to an
external review. The self red team (V0.7.1) produced
one finding (J-0.7.1) that was fixed in V0.6.1. The
external red team produced seven findings. The
difference is not in the volume of attacks (20 vs 14)
but in the diversity of the attacker's assumptions.

The FREEZE itself is a record: it states what will be
fixed, in what order, and why. If the plan turns out
to be wrong, the record will show it.

---

**Status**: PLANNED
**Date**: 2026-10-01
**Author**: Ahmed Ait Zaouit
