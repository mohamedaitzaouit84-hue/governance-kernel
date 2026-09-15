# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| V0.5    | Yes (current) |
| V0.4    | Yes (regression baseline) |
| V0.3    | No |
| < V0.3  | No |

## Reporting a Vulnerability

This project is a governance kernel for AI agents.
Security matters and reports are treated seriously.

**Do NOT open a public issue for security vulnerabilities.**

Send a private report to:

  mohamedaitzaouit84-hue@users.noreply.github.com

Please include:

1. Description of the vulnerability
2. Steps to reproduce (minimal)
3. Affected component (kernel / authorization / agents / ...)
4. Estimated severity (Low / Medium / High / Critical)
5. Proof-of-concept code if safe to share

## Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgement | 72 hours |
| Initial assessment | 7 days |
| Fix or mitigation | 30 days |
| Public disclosure | coordinated with reporter |

The author is one person, on a phone, with zero budget.
Timelines are targets, not guarantees. Transparency is guaranteed.

## Scope

In scope:

- Authorization bypass (permission_gate, v05_gate, policy_engine)
- Confused Deputy attacks
- Invariant bypass in agents
- Audit chain tampering
- Kill switch bypass
- Ed25519 signature forgery
- Hash collision attacks on append_only_log
- State leak between agents
- Trust manipulation (P-L1)
- Capability escalation (P-Q8, P-Q11)

Out of scope:

- Attacks requiring physical access to the device
- Attacks requiring the owner private key
- Social engineering of the author
- Denial of service via resource exhaustion
  (by design, resource_governor applies)
- Issues in third-party platforms (GitHub, Termux)

## Recognition

Valid reports will result in:

- Credited in release notes (unless the reporter prefers anonymity)
- Listed in docs/SECURITY_CREDITS.md (to be created)
- Acknowledged in any future publication

No monetary bounty is available (zero-budget project).
Recognition is given in full.

## Philosophy

This project follows a practice of pre-registered thresholds
(see docs/FREEZE_v0.5.md section 7).

Every security claim is accompanied by a reproducible test
in tests/gate_vNN/.

If you find a claim without a corresponding test, that is itself
a documentation vulnerability. Please report it.

## Integrity

This policy is bound by docs/OPENING.md (Integrity Protocol).
No claims beyond what tests demonstrate. No decoration.

## Contact

Ahmed Ait Zaouit
mohamedaitzaouit84-hue@users.noreply.github.com
Morocco
