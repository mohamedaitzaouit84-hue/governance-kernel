# Contributing to Governance Kernel

Thank you for your interest. This document explains how
to contribute to the project.

---

## Before You Start

Read these files first:

  1. docs/HANDOVER.md        — project state
  2. CHARTER.md              — 10 binding principles
  3. docs/OPENING.md         — integrity protocol
  4. docs/RED_TEAM_PROTOCOL.md — if reporting security issues

The project is small and opinionated. The rules below are
not negotiable. They are why the project has a clean
audit trail.

---

## The 8 Golden Rules

  1. Freeze before code
  2. Pre-registered thresholds
  3. Failures logged before fixes
  4. Kernel Untouched (except declared exceptions)
  5. Minimal-dependency (currently 2: cryptography, pyyaml)
  6. No post-hoc adjustment
  7. Every number sourced (with unit)
  8. Honesty about limits

Any contribution that violates these rules will be
rejected. This is not personal.

---

## What You Can Contribute

### 1. Bug Reports

Open a GitHub issue with:

  - What you expected
  - What happened
  - How to reproduce (minimal steps)
  - Your environment (OS, Python version)
  - Any relevant logs

Bug reports on **protected files** (see docs/FREEZE_v0.7.md
§0) require a FREEZE declaration in the issue before a fix
can be merged. Do not submit a fix for a protected file
without first opening an issue that describes a FREEZE.

### 2. Security Findings

Do NOT open a public issue. See SECURITY.md.

Private channel:
  mohamedaitzaouit84-hue@users.noreply.github.com

Red Team findings: see docs/RED_TEAM_PROTOCOL.md.

### 3. Documentation Improvements

Typos, clarity, missing context — welcome. Open a PR.

### 4. Test Coverage

New tests for existing behavior are welcome, as long as:

  - They pass on all three environments (CI, Colab, Termux)
  - They do not modify protected files
  - They do not weaken existing thresholds

### 5. New Features

New features go through a FREEZE. Before writing code:

  1. Open an issue describing the feature.
  2. The author reviews and decides whether to FREEZE.
  3. If frozen, a FREEZE document is written first.
  4. Then code.

Unilateral feature PRs will be closed (with explanation).

---

## The Workflow

Every contribution follows this flow:

  1. Fork the repository.
  2. Create a branch (name it after the finding/feature).
  3. Make small, focused changes.
  4. Test locally:
       python bootstrap.py
       python tests/gate_v05/run_all.py
       python tests/gate_v07/run_all.py
     Expected: 5/5 + 19/19.
  5. Commit with a clear message.
  6. Push to your fork.
  7. Open a Pull Request.

CI will run automatically:
  - Test Suite (Python 3.11, 3.12, 3.13)
  - Draft PDF (if paper.md changed)

Both must pass before review.

---

## Commit Messages

Use a short prefix:

  fix(scope): ...      — a bug fix
  feat(scope): ...     — a new feature (requires FREEZE)
  docs(scope): ...     — documentation only
  test(scope): ...     — tests only
  chore(scope): ...    — housekeeping

Example:

  fix(bootstrap): verify pub/priv consistency

  Sub-bug A: owner_key.pub was not re-derived from
  owner_key.priv. Now it is, with a MATCH check.

  Closes J-0.8.43.

Reference findings by their JOURNEY ID.

---

## What Is Not Accepted

  - Modifications to kernel/ without a FREEZE
  - Modifications to any file in ALLOWED_EXCEPTIONS
    without a FREEZE
  - "Zero-dependency" claims (the project has 2 dependencies)
  - Post-hoc threshold adjustments
  - Changes that make V0.5 or V0.7 non-idempotent
  - Adding an LLM to the kernel loop (see FREEZE_v0.6_LLM_ABANDONED)
  - Adding new external dependencies (unless justified in a FREEZE)

---

## AI-Assisted Contributions

The project itself uses AI assistance (see AUTHORS.md).
AI-assisted contributions are welcome, provided that:

  - The contributor understands every line they submit.
  - The AI's role is disclosed in the PR description.
  - The contributor is responsible for correctness and
    for compliance with the 8 Golden Rules.

The same standard applies to all contributions.

---

## Code of Conduct

Be technical, be honest, be specific.

Disagreement is welcome. Disrespect is not.

Personal attacks, harassment, or bad-faith reports
will result in the contribution being rejected and
the contributor being blocked.

---

## Recognition

Contributors are credited:

  - In commit messages
  - In AUTHORS.md (if they consent)
  - In release notes, when relevant
  - In arXiv preprints, for substantial findings

The project has no budget. Recognition is academic,
not financial.

---

## Questions

For general questions: GitHub Issues.
For security issues: SECURITY.md.
For red team: docs/RED_TEAM_PROTOCOL.md.

---

**Thank you. The project exists because the rules
protect the work from being diluted.**
