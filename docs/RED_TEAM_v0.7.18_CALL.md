# Red Team Call — Governance Kernel v0.7.18

**Status**: OPEN
**Opened**: 2026-10-01
**Close**: 2026-11-30
**Protocol**: docs/RED_TEAM_PROTOCOL.md

---

## What Is This

`Governance Kernel` is a deterministic governance layer
for AI agents. It sits *beneath* the agent and decides
permissions, trust levels, and resource bounds *before*
any action is executed.

The kernel is ~9,300 lines of Python, with two external
dependencies (cryptography, pyyaml). It passes 54/54
adversarial prompts (PRI = 1.0000) and 29 gates across
V0.5-V0.7.

The author's self red team (V0.7.1) attempted 20 attacks
across 5 categories, blocked 18, and documented 2 known
limitations. The report explicitly states:

  "Self-red-team is NOT equivalent to external red team."
  "External red team remains the strongest missing validation."

**This call answers that gap.**

## What We Want

You are invited to **break the kernel**.

Not the host OS. Not the Python interpreter. Not Ed25519.
The kernel's logic, its state machines, its signed
policies, its audit chain, its trust ladder.

If you find a way to:

  - impersonate a subject
  - bypass delegation revocation
  - forge a policy signature
  - truncate the audit chain undetected
  - starve the resource governor
  - bypass the kill switch
  - poison the semantic memory graph
  - escalate an agent's privileges at runtime
  - manipulate multi-agent consensus

...then you have found something the author could not see.

## Scope

In scope:
  - kernel/, kernel/separation/
  - authorization/
  - policy/
  - control/
  - audit/
  - memory/
  - agents/, agents/multi/

Out of scope:
  - host OS, Python, cryptography primitives
  - physical access, social engineering
  - attacks requiring modifying protected files without
    declaring a FREEZE

Full scope: docs/RED_TEAM_PROTOCOL.md §2-§3.

## How to Report

Private channel (preferred):
  mohamedaitzaouit84-hue@users.noreply.github.com

Public channel (for non-security discussion):
  GitHub Issues

Format:
  [Red Team v0.7.18] <short description>

Full format: docs/RED_TEAM_PROTOCOL.md §6.

## What You Get

  - Your finding logged in docs/JOURNEY.md (J-0.8.x)
  - Credit in commit message, report, and release notes
  - Optional: AUTHORS.md entry
  - Optional: co-authorship on any arXiv preprint

What we cannot offer:
  - Money (the project has no budget)
  - Conference travel
  - Hardware

This is stated upfront. No surprises.

## Timeline

  Phase 1 (announcement):     1 week
  Phase 2 (active review):    4 weeks
  Phase 3 (report + fixes):   2 weeks
  Phase 4 (public writeup):   1 week

Approximately 8 weeks from this announcement.

## Rules

  - Respect responsible disclosure (private first)
  - Do not attack host infrastructure
  - Report in good faith, including negative results
  - Anonymity is allowed and respected

Full rules: docs/RED_TEAM_PROTOCOL.md §7-§10.

## Reference

Prior self red team (V0.7.1):
  docs/RED_TEAM_v0.6.md
  docs/FREEZE_v0.7.1_red_team.md

The prior report's "Threats to Validity" applies in full.
External review is the next step.

## Why Now

The project is at v0.7.18. It is verified across three
environments (CI, Colab, Termux). It has no external
review yet. The author chose to invite one before
building the SDK, because:

  "SDK first risks building an interface on top of a
   foundation that hasn't been properly stressed."
  — u/AltruisticPainter365, r/kubernetes

That comment is the direct origin of this call.

## Contact

Author: Ahmed Ait Zaouit
GitHub: mohamedaitzaouit84-hue
ORCID:  0009-0007-3278-5577
Repo:   https://github.com/mohamedaitzaouit84-hue/governance-kernel

---

**If you break something, the author wants to know.
If you cannot, that is also information.
Both outcomes are recorded.**
