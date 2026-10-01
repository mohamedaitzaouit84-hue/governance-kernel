# Red Team Report — v0.7.18 (AI-Assisted)

**Date**: 2026-10-01
**Target**: Governance Kernel v0.7.18 (HEAD b709e86)
**Method**: AI-assisted (Claude: 3 rounds, 14 attacks;
            Kimi: 1 surgical round + Termux verification)
**Result**: 6 CRITICAL, 3 PARTIAL, 3 BLOCKED (verified)
**Reported by**: Claude (Anthropic) + Kimi + author
**Logged**: J-0.8.50 through J-0.8.58
**Related**: docs/SECURITY_MODEL.md, docs/RED_TEAM_v0.6.md

---

## 1. Executive Summary

Governance Kernel v0.7.18 was tested by an AI-assisted
red team across three rounds (14 attacks total). Four
CRITICAL findings were identified, all of which share a
single root: the kernel trusts files that a same-user
process can modify, without signature or external anchor.

Specifically:

  - The audit chain can be rewritten by recomputing
    hashes (J-0.8.50).
  - The signed checkpoints can be re-signed by the same
    attacker (J-0.8.51), because the signing key is
    readable (J-0.8.53).
  - The kill switch can be disabled by deleting a file
    (J-0.8.52).
  - The owner private key is stored unencrypted
    (J-0.8.53).

Three PARTIAL findings extend the same theme:

  - bootstrap.py re-signs tampered policies
    (J-0.8.54).
  - subjects.json is unsigned and can be tampered
    without detection (J-0.8.55).
  - The audit log's tail can be truncated without
    detection (J-0.8.56).

**No finding invalidates the V0.4-V0.7 gate claims.**
The kernel loop, the agents, the consensus, and the
delegation mechanism all pass their tests. The findings
concern the layers *around* the kernel: the trust base,
the audit trail, the control plane, and the policy
distribution.

The findings are documented in docs/JOURNEY.md
(J-0.8.50-56) and analysed against a threat model in
docs/SECURITY_MODEL.md.

## 2. Method

**Agent**: Claude (Anthropic).
**Environment**: Google Colab (Linux, Python 3.13).
**Protocol**: docs/RED_TEAM_PROTOCOL.md.
**Rounds**: 3, sequential.

Each round was a Python script (per-round, per-attack)
produced by Claude in response to the previous round's
results. The scripts were executed by the author on
Copies of the repository at /content/atk_<name>. No
external infrastructure was touched.

The author reviewed each script before execution. No
attack was included in this report without being
reproduced locally.

## 3. Attacks and Results

### Round 1

| # | Attack | Result |
|---|--------|--------|
| A1 | Policy laundering via bootstrap | PARTIAL |
| A2 | Trust escalation via subjects.json | INSPECT |
| A3 | Kill-flag spoof | BLOCKED (later withdrawn) |
| A4 | Key theft -> forged policy | CRITICAL |
| A5 | Audit chain tamper (truncate/reorder) | PARTIAL |

### Round 2

| # | Attack | Result |
|---|--------|--------|
| A2b | Role+trust escalation in subjects.json | PARTIAL |
| A3b | Kill-flag toggle (existence-only check) | INSPECT |
| A5b | Full audit chain rewrite (re-hash) | CRITICAL |

### Round 3

| # | Attack | Result |
|---|--------|--------|
| A3c | Kill switch delete + pre-lock + garbage | CRITICAL |
| A5c | Checkpoint forgery | CRITICAL |
| Sep | kernel/separation static analysis | INSPECT (no leak found) |
| Gate | Direct gate attacks (harness incomplete) | INSPECT |
| FA | FileAgent path traversal (harness incomplete) | INSPECT |

### Summary

  - 14 attacks attempted
  - 4 CRITICAL
  - 3 PARTIAL
  - 1 BLOCKED (withdrawn by the red team as too weak)
  - 1 INSPECT (round 3, static analysis: no leak)
  - 5 no-finding / harness incomplete

## 4. Findings

### 4.1 J-0.8.50 — Audit chain rewrite (CRITICAL)

An attacker who can write logs/audit.jsonl can rewrite
the whole chain by recomputing hashes. The chain is a
hash chain, not a signature chain. `integrity.py`
returns rc=0 on the forged chain.

### 4.2 J-0.8.51 — Checkpoint forgery (CRITICAL)

The checkpoints are Ed25519-signed, but the signing key
is readable by the same attacker (J-0.8.53). Therefore
the attacker can regenerate matching checkpoints.

### 4.3 J-0.8.52 — Kill switch bypass (CRITICAL)

`is_active()` is `FLAG.exists()`. Deleting
control/kill.flag disables the switch. Additionally:

  - A pre-set flag ("{}" or "garbage") makes
    `trigger()` a no-op (returns False, appends no
    audit record).
  - A garbage flag makes `status()` crash with
    JSONDecodeError.

### 4.4 J-0.8.53 — Unencrypted owner key (CRITICAL)

identity/owner_key.priv is stored unencrypted with
mode 0o600. The root of trust is protected only by
file permissions.

### 4.5 J-0.8.54 — Policy laundering via bootstrap (PARTIAL)

bootstrap.py re-signs default.yaml whenever the
signature fails to verify. An attacker who modifies
the YAML can then run bootstrap to obtain a valid
signature.

### 4.6 J-0.8.55 — subjects.json unsigned (PARTIAL)

authorization/subjects.json has no signature.
Tampering with roles and trust values persists
across bootstrap.

### 4.7 J-0.8.56 — Audit tail truncation (PARTIAL)

Deleting the last N records from logs/audit.jsonl is
not detected. The hash chain does not anchor the
length.


### 4.8 J-0.8.57 — resource_governor.reset() unprivileged (CRITICAL)

control/resource_governor.py exposes:

    def reset():
        if STATE.exists():
            STATE.unlink()

No signature, no audit, no authorization check.
Verified 2026-10-01 in Termux:

    state_before = True (forced)
    rg.reset()
    state_after  = False

Any process can erase the governor's state and
escape resource limits silently.

### 4.9 J-0.8.58 — rotation_manifest.jsonl unsigned (CRITICAL)

audit/rotation.py writes logs/rotation_manifest.jsonl
at every rotation. The manifest links the previous
log file to the new one (previous_last_hash and
new_genesis_hash). It has no Ed25519 signature and
no hash chain. In combination with J-0.8.50, the
'chain across rotation' property is unverifiable.

## 5. What Was NOT Tested

The following were not part of this red team:

  - Direct gate attacks (the harness in round 3 did
    not complete; the SIG line was never adapted).
  - FileAgent path traversal (same: harness incomplete).
  - Delegation replay (discovery only).
  - Unicode action names (harness incomplete).
  - kernel/separation behavioral leakage (static only).
  - resource_governor.reset() and audit/rotation.py
    cleanup paths.
  - Side channels (timing, power).

The absence of these attacks means the "no finding"
result in those areas is not established. They are
listed as open questions.

## 6. Comparison with Self Red Team (V0.7.1)

| Metric | V0.7.1 (self) | v0.7.18 (AI-assisted) |
|--------|---------------|-----------------------|
| Attacks | 20 | 14 |
| Blocked | 18 | 1 (withdrawn) |
| Partial | 0 | 3 |
| Critical | 0 | 4 |
| Findings logged | 1 (J-0.7.1) | 7 (J-0.8.50-56) |
| Kernel untouched | Yes | Yes |

The self red team's 18/20 "blocked" rate was against
attacks the same author wrote. The AI-assisted red
team, working from the public protocol without
access to the code base at first, found attacks the
author had not considered. This is the structural
difference the self red team itself warned about:

  "Self-red-team is NOT equivalent to external red
   team. External red team remains the strongest
   missing validation."

## 7. Recommendations

**In priority order** (see FREEZE_v0.7.19 for details):

  1. Encrypt the owner key with a passphrase
     (J-0.8.53). This is the root fix; J-0.8.51 and
     J-0.8.53 are combined here.
  2. Sign every audit record (J-0.8.50).
  3. Anchor the audit head hash externally after each
     release (J-0.8.50, J-0.8.56).
  4. Sign subjects.json (J-0.8.55).
  5. Make bootstrap require explicit consent to
     re-sign policies (J-0.8.54).
  6. Store kill switch state as a signed audit record
     (J-0.8.52).

## 8. Threats to Validity

  - The red team is AI-assisted, not human. The AI is
    Claude (Anthropic); it may have systematic biases.
  - Only three rounds were run. More rounds might have
    found more.
  - The attacks are not exhaustive: kernel/separation
    was tested statically only; the direct gate
    harness never completed.
  - The threat model (docs/SECURITY_MODEL.md) was
    written *after* the findings. A pre-registered
    threat model might have framed the findings
    differently.
  - No formal methods were used. Everything here is
    behavioural.

## 9. Reproduction

Each attack is reproducible from the raw scripts
(not included here; see JOURNEY.md entries for
commands). The high-level steps are:

  - Clone v0.7.18.
  - Run bootstrap.py.
  - Copy the tree to /content/atk_<name>.
  - Execute the attack script.
  - Compare the observed behaviour with the finding.

## 10. Honest Statement

The kernel's V0.4-V0.7 gate claims were not falsified.
The findings are about the trust base, not about the
gate logic. The kernel does what it says it does;
what it says it does not include defending against a
same-user attacker.

That gap is now documented, in JOURNEY.md (J-0.8.50-58)
and in SECURITY_MODEL.md.

---

**Red Team COMPLETE**
**Two AI systems + direct verification**
**9 findings: 6 CRITICAL, 3 PARTIAL**
**Kernel untouched (G0.ZZ verified on every commit)**
**Next: FREEZE_v0.7.19 (fix plan)**
