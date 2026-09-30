---
title: 'Governance Kernel: A deterministic governance layer for AI agent actions'
tags:
  - Python
  - AI governance
  - AI agents
  - agent actions
  - deterministic governance
  - reproducibility
authors:
  - name: Ahmed Ait Zaouit
    orcid: 0009-0007-3278-5577
    affiliation: 1
affiliations:
  - name: Independent researcher, Morocco
    index: 1
date: 30 September 2026
bibliography: paper.bib
---

# Summary

`Governance Kernel` is a deterministic governance layer that runs
*before* AI agents act. In contrast to post-hoc monitoring systems,
which observe agent behavior and correct it after the fact, the
kernel decides permissions, trust levels, and resource bounds
before any action is executed. The kernel is written in pure
Python with two external dependencies (`cryptography` for Ed25519
signatures, `pyyaml` for signed policy files), and it provides:

- **Separation of concerns** between information, policy, and
  execution nodes (`kernel/separation/`), verified in V0.3.
- **Signed policy files** (YAML with Ed25519 signatures
  [@ed25519] over the file hash, which itself uses SHA-256
  [@sha256]) that a kernel refuses to load when the signature is
  invalid or missing.
- A **hash-chained audit log** where each record commits to the
  previous one, so any tampering is detectable.
- A **kill switch** with a persistent on-disk marker, verified in
  G0.17.
- A **resource governor** that bounds cycle time, memory, and
  throughput per subject.
- **Multi-agent consensus and delegation primitives** (V0.6 and
  V0.7), including Sybil resistance, collusion handling, and
  protocol-bypass checks.
- A **trust ladder** that increases or decreases a subject's
  trust score based on the outcomes of its governed actions.

The kernel is verified across three environments — Termux
(Android), GitHub Actions (Python 3.11, 3.12, 3.13), and Google
Colab — with pre-registered thresholds and no post-hoc adjustment.
Its V0.4 attack suite reports 54/54 blocked prompts against a
54-prompt adversarial set, with a Prompt Resistance Index (PRI) of
1.0000, and outperforms a static-policy baseline on the
*confused deputy* category by a margin of +9.

`Governance Kernel` is designed as a **kernel**, not a framework:
it is meant to sit beneath the agent, not to replace it.

# Statement of Need

Modern AI safety tooling has evolved along two dominant axes:
LLM-centric approaches (NeMo Guardrails [@nemo2024], Guardrails AI
[@guardrails_ai2024]) that validate model outputs, and
general-purpose policy engines (OPA [@opa2024], Cedar [@cedar2024])
that make allow/deny decisions about requests. Neither axis
addresses the governance of *agent actions*: the sequence of
state-changing operations an autonomous agent chooses to perform.

A 2026 PRISMA review of responsible agentic AI governance
[@prisma2026] concluded that the field lacks "adaptive governance
constructs able to adjust to the quickly changing AI functions".
A Springer review of 33 studies [@governance_springer2026]
identified three methodological gaps: the absence of explainability
in raw evidence, the absence of standards for audit-grade evidence,
and the ambiguity of accountability in multi-agent systems. A 2026
study of healthcare agents [@healthcare2026] found that even with
a 30-item governance framework, a major hospital scored 22%.

Recent industrial efforts such as NVIDIA OpenShell + Sentry
[@openshell2026] move in the right direction by enforcing policy at
the silicon level. Their own documentation, however, states that
"a passing result does not establish least privilege or semantic
safety" and that "the checks lack context, so a throwaway
repository and a production one look the same".

`Governance Kernel` addresses this gap by providing a *pre-action*
decision layer with three properties that the existing tools do
not combine:

1. **Agent-action governance** (not LLM output validation, not
   generic request authorization).
2. **Audit-grade evidence** built from hash-chained records with
   a defined granularity, coverage, and integrity contract.
3. **Reproducibility by construction** — every threshold is
   pre-registered, every failure is logged before its fix, and
   every release is verified against three independent
   environments.

The project is intended for two audiences: researchers who need a
reference implementation against which to measure governance
mechanisms, and practitioners who need a minimal, dependency-light
kernel they can embed beneath an existing agent stack.

# Acknowledgements

The author thanks the Open Source community for the cryptographic
and serialization primitives on which this work depends, and the
maintainers of GitHub Actions and Google Colab for providing free
access to reproducible test environments. Sections of the code and
documentation were drafted with an AI assistant under the
methodology described in `docs/OPENING.md`; all design decisions,
review, and approvals remain human.

# References
