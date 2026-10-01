# Red Team Protocol — Governance Kernel v0.7.18

**Version**: 1.0
**Date**: 2026-10-01
**Target**: v0.7.18 (tag), HEAD as of this document
**Status**: OPEN for external review
**Related**: docs/RED_TEAM_v0.6.md (self red team, V0.7.1)

---

## 1. Purpose

This document defines the rules of engagement for an
external Red Team review of Governance Kernel. The goal is
to surface assumptions that the author cannot see because
he wrote the code.

The author's own red team (V0.7.1, 20 attacks, 5 gates) is
documented in docs/RED_TEAM_v0.6.md. It explicitly notes:

  "Self-red-team is NOT equivalent to external red team."
  "External red team remains the strongest missing validation."

This protocol answers that gap.

## 2. What Is In Scope

The Red Team may attempt to break any of the following:

  - kernel/               (the governance loop)
  - kernel/separation/    (V0.3 info/policy/node split)
  - authorization/        (subjects, branches, delegation)
  - policy/               (signed policy files, policy store)
  - control/              (kill switch, resource governor)
  - audit/                (hash-chained log, append-only)
  - memory/               (episodic + semantic, gate)
  - agents/               (file, compute, query, base)
  - agents/multi/         (consensus, delegation, coordination)

Any of these may be attacked via:
  - logic flaws in the invariants they claim to enforce
  - trust-boundary confusion
  - signature or hash verification weaknesses
  - state-machine inconsistencies
  - timing or race conditions (single-threaded assumption)
  - denial-of-service at the kernel layer
  - information leaks across separation boundaries

## 3. What Is Out of Scope

The following are NOT part of this review:

  - The host OS (Linux/Android/Termux)
  - The Python interpreter (CPython 3.11-3.13)
  - The cryptographic primitives (Ed25519, SHA-256) —
    assume they work as specified
  - Physical access attacks (device theft, memory dumps)
  - Social engineering of the author
  - Attacks that require modifying files in ALLOWED_EXCEPTIONS
    without declaring a FREEZE (see docs/FREEZE_v0.7.18.md)

The review focuses on the kernel's logic, not on the
environment in which it runs.

## 4. Attack Surfaces (Non-Exhaustive)

The following are starting points. They are NOT the
complete list, and the Red Team is encouraged to explore
beyond them.

### 4.1 Kernel Separation (V0.3)
  - Can information leak from a Policy node to an
    Information node?
  - Can the Node layer influence the Policy layer?

### 4.2 Authorization
  - Can a subject impersonate another subject?
  - Can a branch exceed its declared permissions?
  - Can delegation be abused (replay, escalation, revocation
    bypass)?

### 4.3 Policy
  - Can a signed policy be replaced without detection?
  - Can the .sig be replayed across policy files?
  - What happens if default.yaml is modified but .sig is not?

### 4.4 Control
  - Can the kill switch be bypassed?
  - Can the resource governor be starved or flooded?
  - Can control/kill.flag be written by an unauthorized process?

### 4.5 Audit
  - Can a record be deleted or reordered without detection?
  - Can a hash collision be forced?
  - What happens if the log is truncated mid-chain?

### 4.6 Memory
  - Can memory:write be exercised without the role?
  - Can the semantic graph be poisoned?
  - Can memory entries cross subject boundaries?

### 4.7 Agents (V0.5)
  - Can an agent escalate privileges at runtime?
  - Can an isolated agent still act?
  - Can the invariant checker be defeated?

### 4.8 Multi-Agent (V0.6/V0.7)
  - Can consensus be manipulated by a colluding bloc?
  - Can Sybil identities be created without registration?
  - Can a proposal be resolved twice?
  - Can timing races produce inconsistent state?

## 5. Success Criteria

Every attack is classified as one of:

  BLOCKED     The kernel prevented the attack. Expected
              behavior. No action required.

  PARTIAL     The attack partially succeeded (e.g. some
              steps bypassed, but not all). Findings are
              recorded. Design decision required.

  CRITICAL    The attack fully succeeded. A JOURNEY
              finding is opened IMMEDIATELY (before any fix).
              The affected gate may be re-opened.

  NOT-YET     The attack requires capabilities outside the
              scope (e.g. physical access). Not counted.

The overall Red Team report will state:

  - N attacks attempted
  - N blocked
  - N partial
  - N critical
  - Findings logged (with IDs)
  - Kernel modifications (0 or more, declared in a FREEZE)

## 6. Reporting Format

Reports are submitted as a GitHub issue OR a private
email (see §7) with the following structure:

    Title:    [Red Team v0.7.18] <short description>
    Category: <which section of §4>
    Attack:
      - What was attempted
      - Why it should work
      - How to reproduce (minimal)
    Result:   BLOCKED / PARTIAL / CRITICAL / NOT-YET
    Evidence: commands, logs, screenshots, PoC code
    Impact:   what breaks if successful

Anonymity is allowed. Use a pseudonym or a fresh GitHub
account. The review is about the kernel, not about the
reviewer.

## 7. Disclosure Policy

Vulnerabilities are NOT to be publicly disclosed before
they are fixed.

Recommended flow:

  1. Private report to the author:
       mohamedaitzaouit84-hue@users.noreply.github.com

  2. The author acknowledges within 7 days.

  3. The finding is logged in JOURNEY.md (visible in the
     public repo) under a new J-0.8.x ID.

  4. A fix is proposed, reviewed, and committed.

  5. A public writeup credits the reporter (unless they
     prefer anonymity).

Public disclosure before step 4 is considered a violation
of responsible disclosure.

## 8. Recognition

Every valid finding is:

  - logged in docs/JOURNEY.md with a J-0.8.x ID
  - credited in the commit message
  - credited in docs/RED_TEAM_v0.7.18.md (report)
  - credited in the corresponding GitHub Release notes

The author is willing to:

  - Add the reporter to AUTHORS.md (if they consent)
  - Co-authorship on any arXiv preprint that includes
    their finding (if they consent)

The author CANNOT offer:

  - Monetary compensation
  - Conference travel
  - Hardware

The project has no budget. This is stated upfront to
avoid misunderstanding.

## 9. Timeline

  Phase 1 (announcement):     1 week
  Phase 2 (active review):    4 weeks
  Phase 3 (report + fixes):   2 weeks
  Phase 4 (public writeup):   1 week

Total: approximately 8 weeks from announcement.

Extensions are possible if the review surfaces deep
findings. Shorter is welcome.

## 10. Ethics

The Red Team agrees to:

  - Not attack the host infrastructure (GitHub, Zenodo,
    or the author's device)
  - Not attempt social engineering
  - Not use findings for personal or commercial gain
    without prior written agreement
  - Respect responsible disclosure (§7)
  - Report in good faith, including negative results
    (i.e. "I could not break X, here is why")

The author agrees to:

  - Take every report seriously
  - Log findings before fixes (project rule)
  - Not retaliate against honest reports
  - Credit reporters publicly (unless they prefer
    anonymity)

## 11. Reference to Prior Work

The author's self red team (V0.7.1) is documented in:

  docs/RED_TEAM_v0.6.md
  docs/FREEZE_v0.7.1_red_team.md

The current protocol extends that work by inviting
external reviewers. The prior document's "Threats to
Validity" section applies in full:

  - self-red-team has structural bias
  - 20 attacks are not exhaustive
  - categories are conceptual, not formal
  - no cryptographic proof of security
  - time attacks assume single-threaded execution

External review is the next step.

## 12. Contact

Author: Ahmed Ait Zaouit
GitHub: mohamedaitzaouit84-hue
Email:  mohamedaitzaouit84-hue@users.noreply.github.com
ORCID:  0009-0007-3278-5577

For security issues, prefer the private channel.
For general discussion, GitHub issues are fine.

---

**Status**: OPEN
**Opened**: 2026-10-01
**Expected close**: 2026-11-30
