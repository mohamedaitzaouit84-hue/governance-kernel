# OPEN_PROBLEMS.md

**Version**: 0.1
**Date**: 2026-10-08
**Related**: SECURITY_MODEL.md, JOURNEY.md, HANDOVER.md,
              CHARTER.md, docs/FREEZE_v0.7.19.md

## Purpose

This document records problems that are known to be open, in the
same style SECURITY_MODEL.md records the boundary between
"claimed" and "not claimed" for the threat model.

Each problem has:
  - A precise statement
  - The adversary modeled
  - What is NOT claimed
  - What would be claimed if solved (with conditions)
  - Constraints on acceptable solutions
  - An acceptance test

This document does NOT propose solutions.
This document does NOT claim novelty.
This document does NOT list all open problems.

## Background — what exists in the codebase

As of commit 22c589e:

  - Ed25519 signing (seed/root.py): every record, checkpoint,
    and cutoff is signed by the owner key.
  - Multi-state verification (audit/integrity.py): each record
    is classified STRICT_VALID, STRICT_INVALID, STRICT_MISSING,
    or LEGACY_UNVERIFIED. The cutoff is verified against its
    signature before use.
  - Signed cutoff (tools/make_audit_cutoff.py): the boundary
    between legacy and strict is itself signed.
  - Fail-closed on malformed content (audit/append_only_log.py):
    a record missing required fields raises CorruptedAuditLog.

These primitives provide integrity and authenticity of records.
They do NOT provide:
  - Proof that the log was not rewritten after a given time.
  - Proof that the kernel that produced the log is authentic.

## OP-1: Detecting history rewrite after external commitment

### Statement

Given a commitment C = (gk_cmt, prev, seq, hash, pk, ts, sig)
published externally at time T, can an external reviewer at
time T' > T verify that the log at T' contains the committed
prefix?

The commitment includes:
  - seq: number of records at commitment time.
  - hash: chain hash of the record at that seq.
  - pk: raw Ed25519 public key, base64.
  - ts: ISO 8601 UTC timestamp.
  - prev: hash of the previous commitment's canonical form
    (null for the first commitment).
  - sig: Ed25519 signature over the canonical JSON of all
    other fields.

The seq is required. Without it, the reviewer cannot know where
to truncate the log for comparison.

### Adversary

The owner, after T. The owner has full control of the device,
the key, and the repository. They want to modify the audit log
so that the modified log appears legitimate.

Distinct from:
  - An external attacker (out of scope; handled by signed
    records, J-0.8.50).
  - A compromised device (subset of the same problem).

### What is NOT claimed

  - Does NOT prove that the kernel ran. See OP-2.
  - Does NOT detect modifications before the first published
    commitment.
  - Does NOT detect modifications between two commitments,
    until the next commitment is published. Window of
    vulnerability: [T_commit, T_next_commit].
  - If nobody saw C, the old commitment provides no protection.
    A commitment that nobody saved is functionally equivalent
    to no commitment at all.

### What is claimed (if solved)

  - Conditional on at least one independent witness. If at
    least one party independent of the owner saved C at time
    T, then any modification of the log that contradicts C is
    detectable at any later time T'.
  - The guarantee is not cryptographic. It is
    social/distributional: detection depends on the existence
    of a witness who kept a copy.

### What the sig field does and does not do

  - `sig` proves the commitment was emitted by the holder of
    `pk`. It is useful against a third party forging a
    commitment.
  - `sig` does NOT protect against the owner. The owner holds
    `pk` and can sign any commitment, including a fabricated
    one. Protection against OP-1's adversary comes only from
    the witness who kept a copy.

### Constraints on acceptable solutions

  - No trusted third party.
  - No TPM, HSM, or Secure Enclave.
  - No remote attestation service.
  - No blockchain or distributed ledger.
  - No new external dependencies (beyond cryptography and
    pyyaml).

### OP-1.1: The tension in "outside the owner's control"

The constraint "no trusted third party" is in tension with the
requirement that the commitment be published outside the
owner's control. Any "outside" location is by definition a
party.

The table below reframes the tradeoff around a single
question: how many parties must collude to break detection?

| Candidate                         | Trust needed              | Colluders to break |
|-----------------------------------|---------------------------|--------------------|
| Single web archive                | Won't delete              | 1                  |
| Single RFC 3161 TSA               | Won't collude             | 1                  |
| Single social post                | Won't delete              | 1                  |
| Single git hosting release        | Won't delete              | 1                  |
| N posts on N distinct platforms   | Not all collude           | N                  |
| N independent archives            | Not all collude           | N                  |

"Independent" here means: no single authority can compel all
of them. N posts on the same platform collapse to 1 colluder.

No candidate fully eliminates third-party trust. Complete
elimination is impossible under the constraints of OP-1.
This is recorded as an acknowledged limitation, not a solved
subproblem.

### Acceptance test

A reviewer, given:
  - the current logs/audit.jsonl
  - the commitment C obtained from an independent witness
    (not from the owner, not from the owner's repository,
    not from a location the owner controls)

Can verify:
  1. Signature of C over its canonical form.
  2. The record at position seq has chain hash == hash.
  3. The log extends that prefix (records after seq form a
     valid chain starting from hash).
  4. If prev is not null and the previous commitment is
     available, sha256(prev canonical) == C.prev.

And can detect:
  - Any modification to records 0..seq that changes the chain
    hash at seq.
  - Any modification that breaks the chain after seq.
  - Deletion of records before seq.

Does NOT require trusting the owner's device or key. The
public key is part of C. If the owner later rotates the key,
the old C still commits to the old key.

### Critical assumption: the witness path

If the reviewer obtains C from the owner, the owner can present
a fake C' that matches the current (rewritten) log. Detection
is possible only if the reviewer holds a copy of C from a
source the owner cannot alter after the fact.

This is the strongest assumption of OP-1. Without it, no
commitment mechanism provides protection.

### Key rotation

If the owner rotates the key, the old C still commits records
0..seq under the old key. Records after seq, signed under a
new key, are outside the guarantee of C_old.

To cover the transition, the owner must publish a key chain
commitment: a signed statement linking key_old and key_new,
where the transition record itself is committed. A reviewer
can then verify a single unbroken chain from genesis to the
current head across key generations.

Without such a chain, an owner can rotate keys and present a
log whose post-rotation section is unsigned relative to the
pre-rotation commitment. This is J-0.8.59 generalized.

### Commitment format (v1)

One line of JSON, readable, copyable by hand:

    {"gk_cmt":1,"prev":<64 hex or null>,"seq":<int>,
     "hash":"<64 hex>","pk":"<44 base64>","ts":"<ISO 8601 UTC>",
     "sig":"<128 hex>"}

Signature: Ed25519 over the canonical JSON of all fields
except sig:

    json.dumps(obj_without_sig, sort_keys=True,
               separators=(",", ":"))

Rationale for one-line format: a shorter, cleaner form has a
higher probability of being saved by a human witness. That is
the actual guarantee of OP-1.

### Current status

OPEN. Mechanism verified locally (2026-10-08). Not solved.

tools/make_commitment.py and tools/verify_commitment.py exist.
Local tests pass (see Test coverage below). No external
publication has occurred. Without a witness who saved a
commitment, OP-1 provides no protection. The mechanism is a
necessary condition, not a sufficient one.

### Test coverage (as of 2026-10-08)

Verified by test:

  - Verification on an unmodified log: OK.
  - Modification of an early record without re-hashing:
    detected (f).
  - Deletion of an early record: detected (f seq gap).
  - Modification with cascade re-hash + re-sign under the
    owner key: detected (e).
  - Append after the committed seq: allowed (OK).

Not yet verified (recorded as tasks for a future gate G0.46):

  - Truncation of the log after commitment (expected: d).
  - --prev verification across two commitments (expected: g).
  - Forged commitment signature with a non-owner key
    (expected: c).
  - Multi-generation key transition.

Untested properties are not claimed. See "What is NOT claimed"
above for the boundaries that hold regardless of testing.

## OP-2: Proving that the specific kernel executed

### Statement

Given a decision recorded in the audit log, can an external
reviewer prove that the specific version of the kernel
(identified by a hash) produced that decision, and not a
modified kernel that produces the same output?

### Adversary

The owner, after the decision. They claim: "The log is
authentic per OP-1, but the kernel that ran may have been
modified. The log records what the modified kernel did."

### Argument — why this may be impossible under the constraints

There is a distinction between:
  - Log integrity: the log has not been modified.
  - Execution authenticity: the process that produced the log
    is the process claimed.

OP-1 addresses the first. OP-2 addresses the second.

As long as the owner controls the environment in which the
kernel runs, any proof that environment produces can be
forged from within. A modified kernel can produce a log that
is indistinguishable from the log of an unmodified kernel,
given the same inputs, because the log format is not
externally constrained to the kernel's actual behavior.

This argument is not formally proven. A workaround may exist
that the author has not identified.

### What is NOT claimed

  - Does NOT follow from OP-1. OP-1 detects history rewrite;
    OP-2 asks whether the process is authentic.
  - Not known to be solvable under the stated constraints
    (by the author).
  - This is an open problem whose solvability is itself in
    question.

### Constraints on acceptable solutions

  Same as OP-1: no TPM, no remote attestation, no third
  party, no blockchain.

### Acceptance test

Unknown. An open problem whose solvability is in question
cannot have a concrete acceptance test until a candidate
solution exists.

### Current status

OPEN. Not known to be solvable under the stated constraints
(by the author).

## OP-3 (placeholder)

Reserved. No content yet.

## Relationship to findings 0.8.50 - 0.8.62

Statuses below reflect docs/JOURNEY.md as of this draft.
Verify before citing.

| Finding   | Status                     | Relation to OP-1 / OP-2                     |
|-----------|----------------------------|---------------------------------------------|
| J-0.8.50  | FIXED (4dc3bdf + 7c4d448)  | Signed audit records. OP-1 builds on this.  |
| J-0.8.51  | OPEN                       | Checkpoint forgery. Instance of OP-1.       |
| J-0.8.53  | OPEN                       | Unencrypted key. If leaked, OP-1 fails.     |
| J-0.8.59  | OPEN                       | Checkpoint key rotation. Instance of OP-1.  |
| J-0.8.61  | PARTIAL FIX                | Not directly related. Noted for completeness. |
| J-0.8.62  | FIXED (Sprint 6 Phase 2c)  | Fail-closed on malformed records. OP-1 uses. |

Range 0.8.50 - 0.8.62: 3 FIXED, 1 PARTIAL, 9 OPEN.

OP-1 is not a new finding. It is a generalization of the
problem domain that J-0.8.50 and J-0.8.51 partially address.

## What this document does NOT do

  - Does NOT propose solutions.
  - Does NOT claim novelty.
  - Does NOT claim OP-1 or OP-2 are solvable.
  - Does NOT replace SECURITY_MODEL.md.
  - Does NOT list all open problems.
  - Does NOT claim its formulation is unique to this project.

## Revision history

- 2026-10-08: Initial draft.
