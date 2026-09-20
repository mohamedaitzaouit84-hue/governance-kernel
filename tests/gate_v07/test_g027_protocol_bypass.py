"""G0.27 — Protocol Integrity (H29).

Criterion: 4/4 protocol bypass attempts rejected.

Scenarios:
  B1: resolve() called twice on same proposal -> BLOCKED (state check)
  B2: Vote on already-executed proposal -> BLOCKED (is_final)
  B3: Missing MIN_QUORUM with high trust -> REJECTED
  B4: Tie broken without owner signature -> REJECTED

Read-only. No changes to V0.6/V0.6.1 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.proposal import Proposal, ProposalState
from agents.multi.consensus import (
    weighted_vote, resolve, ConsensusError, MIN_QUORUM,
)


def _proposal(i):
    p = Proposal(proposer="proposer_agent", action="x", payload={"i": i})
    p.state = ProposalState.VOTING
    return p


def b1_resolve_twice():
    """B1: resolve() twice on same proposal must raise on 2nd call."""
    p = _proposal(1)
    p.votes = [
        weighted_vote("a", 0.5, p, "accept"),
        weighted_vote("b", 0.5, p, "accept"),
    ]
    resolve(p)
    # Second resolve must raise
    try:
        resolve(p)
        return False  # not blocked
    except ConsensusError:
        return True


def b2_vote_on_executed():
    """B2: resolve() on EXECUTED state must raise."""
    p = _proposal(2)
    p.state = ProposalState.EXECUTED  # simulate post-execution
    try:
        resolve(p)
        return False
    except ConsensusError:
        return True


def b3_quorum_fail_high_trust():
    """B3: single vote with max trust cannot satisfy quorum.
    Must be REJECTED."""
    p = _proposal(3)
    p.votes = [weighted_vote("a", 10.0, p, "accept")]  # 1 vote only
    resolve(p)
    # Quorum (>= 2) fails -> REJECTED
    return p.state == ProposalState.REJECTED


def b4_tie_without_owner():
    """B4: 1.0 accept vs 1.0 reject, no owner -> REJECTED."""
    p = _proposal(4)
    p.votes = [
        weighted_vote("a", 0.5, p, "accept"),
        weighted_vote("b", 0.5, p, "reject"),
    ]
    resolve(p)
    # Tie, no owner -> REJECTED
    return p.state == ProposalState.REJECTED


def main():
    attacks = [
        ("B1 resolve twice", b1_resolve_twice),
        ("B2 vote on executed", b2_vote_on_executed),
        ("B3 quorum fail high trust", b3_quorum_fail_high_trust),
        ("B4 tie without owner", b4_tie_without_owner),
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

    print("  Protocol bypass attacks: {}/{} rejected".format(
        passed, len(attacks)))
    if failed:
        print("  NOT rejected: {}".format(failed))

    if passed == len(attacks):
        print("G0.27: CLOSED ({}/{})".format(passed, len(attacks)))
        return 0
    else:
        print("G0.27: FAILED ({}/{})".format(passed, len(attacks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
