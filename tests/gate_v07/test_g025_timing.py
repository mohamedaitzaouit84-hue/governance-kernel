"""G0.25 — Timing Safety (H27).

Criterion: 3/3 timing attacks rejected.

Scenarios:
  T1: Vote cast BEFORE proposal is created (state check)
  T2: Vote cast AFTER proposal is sealed (is_final check)
  T3: Rapid-fire votes in single cycle — all recorded,
      quorum and weights still enforced.

Method: For T1 and T2 we verify that the protocol correctly
refuses to proceed with invalid states. For T3 we verify that
multiple votes in the same resolution pass produce the
expected weighted outcome (not a race condition).

No threading: consensus is single-threaded by design.
Timing attacks are about STATE, not parallel execution.

Read-only. No changes to V0.6 files.
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


def t1_vote_before_creation():
    """T1: A proposal in PENDING state cannot be resolved.
    Simulates voting before the proposal enters VOTING."""
    p = Proposal(proposer="proposer_agent", action="x", payload={"t": 1})
    # state stays PENDING — not VOTING
    # We attempt to resolve directly
    try:
        resolve(p)
        # resolve() should NOT accept PENDING state
        # Check if it raised the correct error
        return False  # not blocked — fail
    except ConsensusError:
        return True


def t2_vote_after_sealed():
    """T2: A sealed (already-resolved) proposal cannot be
    resolved again."""
    p = _proposal(2)
    p.votes = [
        weighted_vote("a", 0.5, p, "accept"),
        weighted_vote("b", 0.5, p, "accept"),
    ]
    resolve(p)  # first resolution -> sealed
    assert p.is_final(), "proposal should be sealed"

    # Attempt to resolve again
    try:
        resolve(p)
        return False  # not blocked
    except ConsensusError:
        return True


def t3_rapid_fire_votes():
    """T3: Multiple votes in the same resolution pass must
    produce the correct weighted outcome."""
    p = _proposal(3)
    p.votes = [
        weighted_vote("a", 0.3, p, "accept"),
        weighted_vote("b", 0.3, p, "accept"),
        weighted_vote("c", 0.3, p, "reject"),
        weighted_vote("d", 0.3, p, "reject"),
        weighted_vote("e", 0.3, p, "reject"),
    ]
    resolve(p)
    # accept_w = 0.6, reject_w = 0.9 -> REJECTED (correct)
    # Also: quorum satisfied (5 distinct agents)
    return (p.state == ProposalState.REJECTED and
            len(p.votes) == 5)


def main():
    attacks = [
        ("T1 vote before creation", t1_vote_before_creation),
        ("T2 vote after sealed", t2_vote_after_sealed),
        ("T3 rapid fire votes", t3_rapid_fire_votes),
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

    print("  Timing attacks: {}/{} rejected or handled".format(
        passed, len(attacks)))
    if failed:
        print("  NOT handled: {}".format(failed))

    if passed == len(attacks):
        print("G0.25: CLOSED ({}/{})".format(passed, len(attacks)))
        return 0
    else:
        print("G0.25: FAILED ({}/{})".format(passed, len(attacks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
