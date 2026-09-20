"""G0.26 — Trust Bound (H28).

Criterion: 4/4 trust manipulation attacks blocked or capped.

Scenarios:
  M1: trust = 10.0 (huge) -> capped at MAX_WEIGHT_PER_AGENT
  M2: trust = -1.0 (negative) -> BLOCKED
  M3: trust = "abc" (wrong type) -> BLOCKED
  M4: trust = float('inf') -> capped at MAX_WEIGHT_PER_AGENT

Trust comes from agent's own state in V0.5. The protocol does
not enforce trust origin, but must enforce trust bound.

Read-only. No changes to V0.6/V0.6.1 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.proposal import Proposal, ProposalState
from agents.multi.consensus import (
    weighted_vote, ConsensusError, MAX_WEIGHT_PER_AGENT,
)


def _proposal(i):
    p = Proposal(proposer="proposer_agent", action="x", payload={"i": i})
    p.state = ProposalState.VOTING
    return p


def m1_huge_trust_capped():
    """M1: trust = 10.0 -> weight capped at MAX_WEIGHT."""
    p = _proposal(1)
    v = weighted_vote("a", 10.0, p, "accept")
    return v["weight"] == MAX_WEIGHT_PER_AGENT


def m2_negative_trust_blocked():
    """M2: trust = -1.0 -> BLOCKED (ConsensusError)."""
    p = _proposal(2)
    try:
        weighted_vote("a", -1.0, p, "accept")
        return False  # not blocked -> fail
    except ConsensusError:
        return True


def m3_wrong_type_blocked():
    """M3: trust = 'abc' -> BLOCKED (type error or ConsensusError)."""
    p = _proposal(3)
    try:
        weighted_vote("a", "abc", p, "accept")
        # If weighted_vote didn't reject, check if weight is sane
        # It might try float('abc') -> ValueError. Accept any exception.
        return False
    except (ConsensusError, TypeError, ValueError):
        return True


def m4_infinity_capped():
    """M4: trust = inf -> capped at MAX_WEIGHT."""
    p = _proposal(4)
    v = weighted_vote("a", float("inf"), p, "accept")
    return v["weight"] == MAX_WEIGHT_PER_AGENT


def main():
    attacks = [
        ("M1 huge trust capped", m1_huge_trust_capped),
        ("M2 negative trust blocked", m2_negative_trust_blocked),
        ("M3 wrong type blocked", m3_wrong_type_blocked),
        ("M4 infinity capped", m4_infinity_capped),
    ]

    passed = 0
    failed = []
    for name, fn in attacks:
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            print("  {}: EXCEPTION {}".format(name, e))
        if ok:
            passed += 1
        else:
            failed.append(name)

    print("  Trust manipulation attacks: {}/{} blocked or capped".format(
        passed, len(attacks)))
    if failed:
        print("  NOT handled: {}".format(failed))

    if passed == len(attacks):
        print("G0.26: CLOSED ({}/{})".format(passed, len(attacks)))
        return 0
    else:
        print("G0.26: FAILED ({}/{})".format(passed, len(attacks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
