# Security Model — Governance Kernel v0.7.18

**Version**: 1.0
**Date**: 2026-10-01
**Status**: Draft (in response to external red team)
**Related**: J-0.8.50-56, docs/RED_TEAM_v0.6.md

---

## 1. Purpose

This document defines the threat model of Governance
Kernel: what it protects against, what it assumes, and
what it does not protect against.

It exists because the first external red team
(2026-10-01) surfaced several CRITICAL findings that
were correct in their own frame, but whose severity
depends entirely on the threat model. Without a written
model, the conversation about "is this a bug or a
design choice" has no ground.

This document is the ground.

## 2. What the Kernel Protects Against

The kernel enforces **behavioral invariants on agents**:

  - An agent cannot perform an action its role does not
    permit (V0.5, V0.7).
  - An agent cannot exceed its trust-derived weight in
    consensus (V0.6).
  - An agent cannot bypass delegation lifecycle rules
    (V0.7).
  - A prompt-injection attack cannot cause an
    unauthorized action (V0.4).
  - A kill switch, once activated, halts all operations
    (V0.5 G0.17).
  - A resource governor bounds CPU, memory, and
    throughput per subject (V0.7).

These are the properties the project claims and tests.

## 3. Assumptions (Trusted Base)

The kernel trusts:

  A1. The Python interpreter (CPython 3.11-3.13).
  A2. The `cryptography` library's Ed25519 and SHA-256
      implementations.
  A3. The host OS's file permission enforcement
      (chmod, chown, and the file system's access
      control).
  A4. The user account under which the kernel runs.
  A5. The system clock (for timestamps).
  A6. The physical security of the device.

If any of A1-A6 is compromised, the kernel's
guarantees are void. This is not unusual; it is the
standard trust base of any application-level security
system.

## 4. What the Kernel Does NOT Protect Against

### 4.1 Same-User Attacker

Any process running as the same user as the kernel
can read and write any file the kernel reads and
writes. This includes:

  - identity/owner_key.priv  (J-0.8.53)
  - logs/audit.jsonl         (J-0.8.50, J-0.8.56)
  - logs/checkpoints.jsonl   (J-0.8.51)
  - policy/policies/*.yaml   (J-0.8.54)
  - authorization/*.json     (J-0.8.55)
  - control/kill.flag        (J-0.8.52)

The kernel is not designed to protect against this
attacker. The only mitigations available at the
application layer are:

  - Encrypting the owner key with a passphrase.
  - Publishing hashes to an external anchor.
  - Running the kernel in a sandbox separate from
    potential attackers.

None of these are implemented in v0.7.18. They are
listed as fix plans in J-0.8.50-56.

### 4.2 Root / Kernel-Mode Attacker

A root attacker can read memory, modify the
interpreter, and bypass any file permission. No
user-space security system defends against this.

### 4.3 Physical Attacker

Physical access to the device allows cold-boot
attacks, memory dumps, and disk extraction. Out of
scope.

### 4.4 Side-Channel Attacker

Timing, power, and electromagnetic side channels are
not addressed. Out of scope.

### 4.5 Network Attacker

The kernel is not networked. There is no protocol,
no TLS, no session. A network attacker has nothing
to attack in the kernel itself.

### 4.6 Supply-Chain Attacker

The `cryptography` and `pyyaml` packages are assumed
trustworthy. If either is compromised, the kernel is
compromised. Mitigation is outside the project's
scope (pin versions, audit wheels, etc.).

## 5. Mapping of Red Team Findings to This Model

| Finding | In scope? | Severity |
|---------|-----------|----------|
| J-0.8.50 (audit re-hash) | Same-user attacker | CRITICAL if same-user is in scope |
| J-0.8.51 (checkpoint forgery) | Same-user attacker | CRITICAL if same-user is in scope |
| J-0.8.52 (kill switch delete) | Same-user attacker | CRITICAL if same-user is in scope |
| J-0.8.53 (key unencrypted) | Same-user attacker | CRITICAL if same-user is in scope |
| J-0.8.54 (policy laundering) | Same-user attacker | PARTIAL |
| J-0.8.55 (subjects escalation) | Same-user attacker | PARTIAL |
| J-0.8.56 (audit truncation) | Same-user attacker | PARTIAL |

Note: all findings share the same root cause — the
threat model did not explicitly include or exclude
the same-user attacker. This document makes the
choice explicit.

## 6. The Choice

There are two coherent positions:

### Position A — Same-user attacker is OUT of scope

Rationale: the kernel runs on a personal device.
The user's account is assumed to be the user's
trusted environment. A process running as the user
is the user.

Consequences:
  - J-0.8.50-56 are documented limitations, not bugs.
  - No code changes are required for v0.7.19.
  - The fixes become future work for a "production"
    variant (v0.8.x).

### Position B — Same-user attacker is IN scope

Rationale: the kernel claims to be a "governance"
layer. Governance implies independence from the
governed party. If the user's account can rewrite
the audit log, the audit log is not a governance
instrument; it is a log.

Consequences:
  - J-0.8.50-53 require code fixes (see FREEZE_v0.7.19).
  - J-0.8.54-56 require code fixes.
  - The kernel becomes meaningfully different from
    "a set of checks the user could remove".

## 7. Position of v0.7.18

**v0.7.18 adopts Position A.**

The kernel runs on a single-user Android device. The
same-user attacker model is the dominant threat in
that environment (via malicious apps with the same
UID — which is not possible on Android without
root). The project's claim is behavioral, not
adversarial: "the agent does not exceed its role",
not "the user cannot tamper with the log".

This position is recorded explicitly, and it implies:

  - J-0.8.50-56 are documented as **known
    limitations** with respect to Position B.
  - Fixes for Position B are deferred to v0.8.x
    (see FREEZE_v0.7.19 for the plan).
  - The external red team's findings remain valid
    and are not dismissed. They are reclassified:
    not bugs against the stated model, but gaps
    against the stronger model that a reviewer may
    reasonably expect.

## 8. Future Work

The following are planned for v0.8.x:

  - Encrypt the owner key with a passphrase
    (J-0.8.53).
  - Sign every audit record (J-0.8.50).
  - Anchor the audit head hash externally after each
    release (J-0.8.50, J-0.8.56).
  - Sign subjects.json like branches (J-0.8.55).
  - Make bootstrap require explicit consent to re-sign
    policies (J-0.8.54).
  - Store kill switch state as a signed audit record
    (J-0.8.52).

The order reflects dependency: J-0.8.53 (key at rest)
should come first, since J-0.8.51 depends on it.

## 9. Honest Statement

Governance Kernel v0.7.18 is a research artifact.

It has been tested against its stated threat model.
It has been challenged by an external AI-assisted
red team that found 7 findings (4 CRITICAL, 3
PARTIAL) against a stronger threat model. Those
findings are documented, not hidden.

Anyone planning to use the kernel in an
adversarial environment should read J-0.8.50-56
and decide whether their threat model includes
the same-user attacker.

The honest position is: this is what we tested,
this is what we assume, this is what we do not
protect against.

---

**Status**: Draft
**Next**: adopt as stable after external review.
